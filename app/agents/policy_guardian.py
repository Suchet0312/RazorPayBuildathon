from app.domain.enums.failure_category import FailureCategory
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import PolicyDecision, RecoveryPlan
from app.policies.constants import (
    MAX_AUTO_ACTION_AMOUNT,
    MAX_CUSTOMER_CONTACTS,
    MAX_RETRY_ATTEMPTS,
    MIN_RECOVERY_PROBABILITY,
)


AUTOMATED_ACTIONS = {
    RecoveryAction.RETRY_NOW,
    RecoveryAction.RETRY_LATER,
    RecoveryAction.SEND_RECOVERY_LINK,
    RecoveryAction.SUGGEST_ALTERNATE_METHOD,
    RecoveryAction.MANDATE_RETRY,
    RecoveryAction.PROMISE_TO_PAY,
    RecoveryAction.B2B_RECEIVABLES_CHASE,
    RecoveryAction.HINGLISH_VOICE_RECOVERY,
}

RETRY_ACTIONS = {
    RecoveryAction.RETRY_NOW,
    RecoveryAction.RETRY_LATER,
    RecoveryAction.MANDATE_RETRY,
}

CONTACT_ACTIONS = {
    RecoveryAction.SEND_RECOVERY_LINK,
    RecoveryAction.PROMISE_TO_PAY,
    RecoveryAction.HINGLISH_VOICE_RECOVERY,
    RecoveryAction.B2B_RECEIVABLES_CHASE,
}


def evaluate_policy(
    payment: PaymentRiskRecord,
    failure_category: FailureCategory,
    recovery_probability: float,
    recovery_plan: RecoveryPlan,
) -> PolicyDecision:
    action = recovery_plan.action

    # Safe terminal outcome: no execution required
    if action == RecoveryAction.DO_NOTHING:
        return PolicyDecision(
            approved=True,
            reason_codes=["NO_ACTION_REQUIRED"],
            reason="No recovery action is required for this payment.",
        )

    # Safe handoff outcome: no automated external action
    if action == RecoveryAction.ESCALATE_TO_MERCHANT:
        return PolicyDecision(
            approved=True,
            reason_codes=["MERCHANT_ESCALATION_REQUIRED"],
            reason="Case is approved for merchant escalation.",
        )

    # Permanent failures cannot receive automated recovery actions
    if failure_category == FailureCategory.PERMANENT_FAILURE:
        return PolicyDecision(
            approved=False,
            reason_codes=["PERMANENT_FAILURE_BLOCKED"],
            reason="Automated recovery is blocked for permanent failures.",
        )

    # Amount exposure limit
    if (
        action in AUTOMATED_ACTIONS
        and payment.amount > MAX_AUTO_ACTION_AMOUNT
    ):
        return PolicyDecision(
            approved=False,
            reason_codes=["AMOUNT_LIMIT_EXCEEDED"],
            reason="Payment amount exceeds the maximum allowed for automated action.",
        )

    # Minimum recovery probability
    if (
        action in AUTOMATED_ACTIONS
        and recovery_probability < MIN_RECOVERY_PROBABILITY
    ):
        return PolicyDecision(
            approved=False,
            reason_codes=["RECOVERY_PROBABILITY_TOO_LOW"],
            reason="Recovery probability is below the minimum policy threshold.",
        )

    # Retry limit
    if (
        action in RETRY_ACTIONS
        and payment.attempt_count >= MAX_RETRY_ATTEMPTS
    ):
        return PolicyDecision(
            approved=False,
            reason_codes=["MAX_RETRY_LIMIT_REACHED"],
            reason="Maximum retry attempt limit has been reached.",
        )

    # Customer contact limit
    if (
        action in CONTACT_ACTIONS
        and payment.contact_count >= MAX_CUSTOMER_CONTACTS
    ):
        return PolicyDecision(
            approved=False,
            reason_codes=["MAX_CUSTOMER_CONTACT_LIMIT_REACHED"],
            reason="Maximum customer contact limit has been reached.",
        )

    return PolicyDecision(
        approved=True,
        reason_codes=["POLICY_CHECKS_PASSED"],
        reason="Recovery action satisfies all applicable policy checks.",
    )
