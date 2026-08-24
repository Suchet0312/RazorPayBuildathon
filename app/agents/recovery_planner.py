from app.domain.enums.failure_category import FailureCategory
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import Diagnosis, RecoveryPlan


HIGH_RECOVERY_PROBABILITY_THRESHOLD = 0.70
LOW_RECOVERY_PROBABILITY_THRESHOLD = 0.40
REPEATED_ATTEMPTS_THRESHOLD = 2


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
    For the Day 4 MVP, expected recovery value is the priority score.
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

    Final execution authority will belong to the deterministic
    Policy Guardian in Day 5.
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
    """

    reason_codes = list(diagnosis.reason_codes)

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

    # 2. Customer action is required.
    if failure_category == FailureCategory.CUSTOMER_ACTION_REQUIRED:
        return (
            RecoveryAction.SEND_RECOVERY_LINK,
            reason_codes + [
                "CUSTOMER_ACTION_REQUIRED",
                "RECOVERY_LINK_RECOMMENDED",
            ],
            {},
        )

    # 3. Checkout abandonment.
    if failure_category == FailureCategory.CHECKOUT_ABANDONMENT:
        return (
            RecoveryAction.SEND_RECOVERY_LINK,
            reason_codes + [
                "CHECKOUT_ABANDONMENT",
                "RECOVERY_LINK_RECOMMENDED",
            ],
            {},
        )

    # 4. Repeated failures suggest changing the payment approach.
    if payment.attempt_count >= REPEATED_ATTEMPTS_THRESHOLD:
        return (
            RecoveryAction.SUGGEST_ALTERNATE_METHOD,
            reason_codes + [
                "REPEATED_ATTEMPTS",
                "ALTERNATE_PAYMENT_METHOD_RECOMMENDED",
            ],
            {},
        )

    # 5. Temporary failure with high recovery probability.
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

    # 6. Temporary failure with a low number of attempts.
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

    # 7. Low-confidence or ambiguous cases are escalated.
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

    Primary ranking:
        Higher priority_score first.

    Tie breakers:
        1. Higher expected_recovery_value
        2. Higher recovery action value is not considered
        3. Stable payment_id ordering

    The final payment_id tie breaker ensures identical inputs always
    produce the same ordering.
    """

    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate[1].priority_score,
            -candidate[1].expected_recovery_value,
            candidate[0].payment_id,
        ),
    )

