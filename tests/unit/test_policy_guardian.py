from datetime import datetime

import pytest

from app.agents.policy_guardian import evaluate_policy
from app.domain.enums.failure_category import FailureCategory
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import RecoveryPlan


def make_payment(
    *,
    amount: float = 5_000.0,
    attempt_count: int = 0,
    contact_count: int = 0,
) -> PaymentRiskRecord:
    return PaymentRiskRecord(
        payment_id="pay_policy_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        amount=amount,
        currency="INR",
        payment_method="upi",
        status=PaymentStatus.FAILED,
        failure_reason="bank_timeout",
        attempt_count=attempt_count,
        event_timestamp=datetime(2026, 8, 25, 10, 0, 0),
        customer_success_rate=0.9,
        previous_retry_success_rate=0.8,
        contact_count=contact_count,
    )


def make_plan(
    action: RecoveryAction,
) -> RecoveryPlan:
    return RecoveryPlan(
        action=action,
        expected_recovery_value=4_000.0,
        priority_score=4_000.0,
    )


def test_approves_valid_retry_action():
    decision = evaluate_policy(
        payment=make_payment(),
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.8,
        recovery_plan=make_plan(RecoveryAction.RETRY_NOW),
    )

    assert decision.approved is True
    assert decision.reason_codes == ["POLICY_CHECKS_PASSED"]


def test_blocks_permanent_failure():
    decision = evaluate_policy(
        payment=make_payment(),
        failure_category=FailureCategory.PERMANENT_FAILURE,
        recovery_probability=0.9,
        recovery_plan=make_plan(RecoveryAction.RETRY_NOW),
    )

    assert decision.approved is False
    assert "PERMANENT_FAILURE_BLOCKED" in decision.reason_codes


def test_blocks_amount_above_limit():
    decision = evaluate_policy(
        payment=make_payment(amount=20_000.0),
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.9,
        recovery_plan=make_plan(RecoveryAction.RETRY_LATER),
    )

    assert decision.approved is False
    assert "AMOUNT_LIMIT_EXCEEDED" in decision.reason_codes


def test_blocks_low_recovery_probability():
    decision = evaluate_policy(
        payment=make_payment(),
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.3,
        recovery_plan=make_plan(RecoveryAction.RETRY_NOW),
    )

    assert decision.approved is False
    assert "RECOVERY_PROBABILITY_TOO_LOW" in decision.reason_codes


def test_blocks_retry_limit_reached():
    decision = evaluate_policy(
        payment=make_payment(attempt_count=2),
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.8,
        recovery_plan=make_plan(RecoveryAction.RETRY_NOW),
    )

    assert decision.approved is False
    assert "MAX_RETRY_LIMIT_REACHED" in decision.reason_codes


def test_blocks_customer_contact_limit():
    decision = evaluate_policy(
        payment=make_payment(contact_count=1),
        failure_category=FailureCategory.CUSTOMER_ACTION_REQUIRED,
        recovery_probability=0.8,
        recovery_plan=make_plan(RecoveryAction.SEND_RECOVERY_LINK),
    )

    assert decision.approved is False
    assert "MAX_CUSTOMER_CONTACT_LIMIT_REACHED" in decision.reason_codes


def test_approves_do_nothing_as_safe_outcome():
    decision = evaluate_policy(
        payment=make_payment(),
        failure_category=FailureCategory.PERMANENT_FAILURE,
        recovery_probability=0.1,
        recovery_plan=make_plan(RecoveryAction.DO_NOTHING),
    )

    assert decision.approved is True
    assert "NO_ACTION_REQUIRED" in decision.reason_codes


def test_approves_escalation_as_safe_handoff():
    decision = evaluate_policy(
        payment=make_payment(amount=50_000.0),
        failure_category=FailureCategory.PERMANENT_FAILURE,
        recovery_probability=0.1,
        recovery_plan=make_plan(RecoveryAction.ESCALATE_TO_MERCHANT),
    )

    assert decision.approved is True
    assert "MERCHANT_ESCALATION_REQUIRED" in decision.reason_codes