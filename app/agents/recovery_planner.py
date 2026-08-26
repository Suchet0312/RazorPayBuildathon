from app.domain.enums.failure_category import FailureCategory
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import Diagnosis, RecoveryPlan


HIGH_RECOVERY_PROBABILITY_THRESHOLD = 0.70
LOW_RECOVERY_PROBABILITY_THRESHOLD = 0.40
REPEATED_ATTEMPTS_THRESHOLD = 2

# Failure reasons that indicate mandate/recurring payment issues
MANDATE_FAILURE_REASONS = {
    "mandate_rejected",
    "mandate_expired",
    "nach_bounce",
    "ecs_bounce",
    "debit_failed",
    "subscription_failed",
    "subscription_expired",
}

# Failure reasons that indicate B2B / invoice scenarios
B2B_FAILURE_REASONS = {
    "invoice_overdue",
    "b2b_overdue",
    "payment_promised",
    "credit_limit_exceeded",
}


def calculate_expected_recovery_value(
    amount: float,
    recovery_probability: float,
) -> float:
    """
    Calculate the expected monetary value of attempting recovery.

    Formula:
        expected_recovery_value = amount * recovery_probability
    """

    if amount < 0:
        raise ValueError("amount cannot be negative")

    if not 0.0 <= recovery_probability <= 1.0:
        raise ValueError(
            "recovery_probability must be between 0.0 and 1.0"
        )

    return round(amount * recovery_probability, 2)


def calculate_priority_score(
    payment: PaymentRiskRecord,
    recovery_probability: float,
) -> float:
    """
    Priority score is the expected recovery value.
    """

    return calculate_expected_recovery_value(
        amount=payment.amount,
        recovery_probability=recovery_probability,
    )


def plan_recovery_action(
    payment: PaymentRiskRecord,
    failure_category: FailureCategory,
    recovery_probability: float,
    diagnosis: Diagnosis,
) -> RecoveryPlan:
    """
    Select exactly one bounded recovery action.

    This function only recommends an action.
    It does not approve or execute the action.
    """

    expected_recovery_value = calculate_expected_recovery_value(
        amount=payment.amount,
        recovery_probability=recovery_probability,
    )

    priority_score = calculate_priority_score(
        payment=payment,
        recovery_probability=recovery_probability,
    )

    action, reason_codes, action_parameters = _select_recovery_action(
        payment=payment,
        failure_category=failure_category,
        recovery_probability=recovery_probability,
        diagnosis=diagnosis,
    )

    return RecoveryPlan(
        action=action,
        action_parameters=action_parameters,
        reason_codes=reason_codes,
        expected_recovery_value=expected_recovery_value,
        priority_score=priority_score,
    )


def _select_recovery_action(
    payment: PaymentRiskRecord,
    failure_category: FailureCategory,
    recovery_probability: float,
    diagnosis: Diagnosis,
) -> tuple[RecoveryAction, list[str], dict]:
    """
    Deterministically select exactly one allow-listed recovery action.

    Priority order:
      1. Permanent failures → DO_NOTHING
      2. Mandate / recurring failures → MANDATE_RETRY
      3. B2B / receivables failures → B2B_RECEIVABLES_CHASE
      4. Customer action required (promise-to-pay pattern) → PROMISE_TO_PAY
      5. Checkout abandonment → SEND_RECOVERY_LINK
      6. Repeated attempts → SUGGEST_ALTERNATE_METHOD
      7. Temporary + high probability → RETRY_LATER
      8. Temporary + low attempts → RETRY_NOW
      9. Default → ESCALATE_TO_MERCHANT
    """

    reason_codes = list(diagnosis.reason_codes)
    failure_reason = (payment.failure_reason or "").lower().strip()

    # 1. Permanent failures should not trigger automatic recovery.
    if failure_category == FailureCategory.PERMANENT_FAILURE:
        return (
            RecoveryAction.DO_NOTHING,
            reason_codes + [
                "PERMANENT_FAILURE",
                "AUTOMATIC_RECOVERY_NOT_RECOMMENDED",
            ],
            {},
        )

    # 2. Mandate / recurring / subscription failures → MANDATE_RETRY
    if failure_reason in MANDATE_FAILURE_REASONS:
        return (
            RecoveryAction.MANDATE_RETRY,
            reason_codes + [
                "MANDATE_OR_SUBSCRIPTION_FAILURE",
                "MANDATE_RETRY_RECOMMENDED",
            ],
            {
                "retry_sequence": ["T+1h", "T+24h", "T+72h"],
                "notify_customer": True,
            },
        )

    # 3. B2B receivables / invoice overdue → B2B_RECEIVABLES_CHASE
    if failure_reason in B2B_FAILURE_REASONS:
        return (
            RecoveryAction.B2B_RECEIVABLES_CHASE,
            reason_codes + [
                "B2B_INVOICE_OVERDUE",
                "B2B_RECEIVABLES_CHASE_RECOMMENDED",
            ],
            {
                "escalation_levels": ["reminder", "senior_ar", "legal"],
                "days_overdue": 0,
            },
        )

    # 4. Customer action required with multiple failed attempts → PROMISE_TO_PAY
    if (
        failure_category == FailureCategory.CUSTOMER_ACTION_REQUIRED
        and payment.attempt_count >= REPEATED_ATTEMPTS_THRESHOLD
    ):
        return (
            RecoveryAction.PROMISE_TO_PAY,
            reason_codes + [
                "CUSTOMER_ACTION_REQUIRED",
                "REPEATED_ATTEMPTS",
                "PROMISE_TO_PAY_RECOMMENDED",
            ],
            {
                "commitment_window_days": 3,
                "follow_up_enabled": True,
            },
        )

    # 5. Customer action required (first attempt) → SEND_RECOVERY_LINK
    if failure_category == FailureCategory.CUSTOMER_ACTION_REQUIRED:
        return (
            RecoveryAction.SEND_RECOVERY_LINK,
            reason_codes + [
                "CUSTOMER_ACTION_REQUIRED",
                "RECOVERY_LINK_RECOMMENDED",
            ],
            {},
        )

    # 6. Checkout abandonment → SEND_RECOVERY_LINK
    if failure_category == FailureCategory.CHECKOUT_ABANDONMENT:
        return (
            RecoveryAction.SEND_RECOVERY_LINK,
            reason_codes + [
                "CHECKOUT_ABANDONMENT",
                "RECOVERY_LINK_RECOMMENDED",
            ],
            {},
        )

    # 7. Repeated failures → SUGGEST_ALTERNATE_METHOD
    if payment.attempt_count >= REPEATED_ATTEMPTS_THRESHOLD:
        return (
            RecoveryAction.SUGGEST_ALTERNATE_METHOD,
            reason_codes + [
                "REPEATED_ATTEMPTS",
                "ALTERNATE_PAYMENT_METHOD_RECOMMENDED",
            ],
            {},
        )

    # 8. Temporary failure with high recovery probability → RETRY_LATER
    if (
        failure_category == FailureCategory.TEMPORARY_FAILURE
        and recovery_probability >= HIGH_RECOVERY_PROBABILITY_THRESHOLD
    ):
        return (
            RecoveryAction.RETRY_LATER,
            reason_codes + [
                "TEMPORARY_FAILURE",
                "HIGH_RECOVERY_PROBABILITY",
                "RETRY_LATER_RECOMMENDED",
            ],
            {
                "delay_minutes": 30,
            },
        )

    # 9. Temporary failure with a low number of attempts → RETRY_NOW
    if (
        failure_category == FailureCategory.TEMPORARY_FAILURE
        and payment.attempt_count < REPEATED_ATTEMPTS_THRESHOLD
    ):
        return (
            RecoveryAction.RETRY_NOW,
            reason_codes + [
                "TEMPORARY_FAILURE",
                "LOW_ATTEMPT_COUNT",
                "RETRY_NOW_RECOMMENDED",
            ],
            {},
        )

    # 10. Low-confidence or ambiguous cases are escalated.
    return (
        RecoveryAction.ESCALATE_TO_MERCHANT,
        reason_codes + [
            "AMBIGUOUS_RECOVERY_CASE",
            "MERCHANT_REVIEW_RECOMMENDED",
        ],
        {},
    )


def rank_recovery_candidates(
    candidates: list[tuple[PaymentRiskRecord, RecoveryPlan]],
) -> list[tuple[PaymentRiskRecord, RecoveryPlan]]:
    """
    Rank recovery candidates deterministically.

    Primary ranking: Higher priority_score first.
    Tie breakers: higher expected_recovery_value, then stable payment_id.
    """

    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate[1].priority_score,
            -candidate[1].expected_recovery_value,
            candidate[0].payment_id,
        ),
    )
