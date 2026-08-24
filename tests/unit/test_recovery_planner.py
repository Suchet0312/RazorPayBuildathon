from datetime import datetime

import pytest

from app.agents.recovery_planner import (
    calculate_expected_recovery_value,
    calculate_priority_score,
    plan_recovery_action,
    rank_recovery_candidates,
)
from app.domain.enums.failure_category import FailureCategory
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import Diagnosis


def create_test_payment(
    payment_id: str = "pay_test_001",
    amount: float = 5000.0,
    attempt_count: int = 1,
) -> PaymentRiskRecord:
    return PaymentRiskRecord(
        payment_id=payment_id,
        customer_id="cust_test_001",
        merchant_id="merchant_test_001",
        amount=amount,
        currency="INR",
        payment_method="upi",
        status=PaymentStatus.FAILED,
        failure_reason="bank_timeout",
        attempt_count=attempt_count,
        event_timestamp=datetime.now(),
        customer_success_rate=0.90,
        previous_retry_success_rate=0.80,
        contact_count=0,
    )


def create_test_diagnosis() -> Diagnosis:
    return Diagnosis(
        summary="Test diagnosis",
        reason_codes=["TEST_REASON"],
        confidence=0.80,
    )


def test_calculate_expected_recovery_value():
    result = calculate_expected_recovery_value(
        amount=5000.0,
        recovery_probability=0.82,
    )

    assert result == 4100.0


def test_expected_recovery_value_rejects_invalid_probability():
    with pytest.raises(ValueError):
        calculate_expected_recovery_value(
            amount=5000.0,
            recovery_probability=1.5,
        )


def test_permanent_failure_results_in_do_nothing():
    payment = create_test_payment()

    plan = plan_recovery_action(
        payment=payment,
        failure_category=FailureCategory.PERMANENT_FAILURE,
        recovery_probability=0.10,
        diagnosis=create_test_diagnosis(),
    )

    assert plan.action == RecoveryAction.DO_NOTHING
    assert plan.expected_recovery_value == 500.0


def test_customer_action_required_results_in_recovery_link():
    payment = create_test_payment()

    plan = plan_recovery_action(
        payment=payment,
        failure_category=FailureCategory.CUSTOMER_ACTION_REQUIRED,
        recovery_probability=0.70,
        diagnosis=create_test_diagnosis(),
    )

    assert plan.action == RecoveryAction.SEND_RECOVERY_LINK


def test_checkout_abandonment_results_in_recovery_link():
    payment = create_test_payment()

    plan = plan_recovery_action(
        payment=payment,
        failure_category=FailureCategory.CHECKOUT_ABANDONMENT,
        recovery_probability=0.65,
        diagnosis=create_test_diagnosis(),
    )

    assert plan.action == RecoveryAction.SEND_RECOVERY_LINK


def test_repeated_attempts_result_in_alternate_method():
    payment = create_test_payment(
        attempt_count=3,
    )

    plan = plan_recovery_action(
        payment=payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.80,
        diagnosis=create_test_diagnosis(),
    )

    assert plan.action == RecoveryAction.SUGGEST_ALTERNATE_METHOD


def test_temporary_high_probability_results_in_retry_later():
    payment = create_test_payment(
        attempt_count=1,
    )

    plan = plan_recovery_action(
        payment=payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.85,
        diagnosis=create_test_diagnosis(),
    )

    assert plan.action == RecoveryAction.RETRY_LATER
    assert plan.action_parameters["delay_minutes"] == 30


def test_temporary_low_attempt_results_in_retry_now():
    payment = create_test_payment(
        attempt_count=1,
    )

    plan = plan_recovery_action(
        payment=payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.55,
        diagnosis=create_test_diagnosis(),
    )

    assert plan.action == RecoveryAction.RETRY_NOW


def test_priority_score_equals_expected_recovery_value():
    payment = create_test_payment(
        amount=10000.0,
    )

    priority_score = calculate_priority_score(
        payment=payment,
        recovery_probability=0.60,
    )

    assert priority_score == 6000.0


def test_candidates_are_ranked_by_priority_score():
    high_value_payment = create_test_payment(
        payment_id="pay_high",
        amount=10000.0,
    )

    lower_value_payment = create_test_payment(
        payment_id="pay_low",
        amount=5000.0,
    )

    diagnosis = create_test_diagnosis()

    high_value_plan = plan_recovery_action(
        payment=high_value_payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.70,
        diagnosis=diagnosis,
    )

    lower_value_plan = plan_recovery_action(
        payment=lower_value_payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.80,
        diagnosis=diagnosis,
    )

    ranked = rank_recovery_candidates(
        [
            (lower_value_payment, lower_value_plan),
            (high_value_payment, high_value_plan),
        ]
    )

    assert ranked[0][0].payment_id == "pay_high"
    assert ranked[1][0].payment_id == "pay_low"


def test_candidate_ranking_is_deterministic_for_equal_scores():
    payment_b = create_test_payment(
        payment_id="pay_b",
        amount=5000.0,
    )

    payment_a = create_test_payment(
        payment_id="pay_a",
        amount=5000.0,
    )

    diagnosis = create_test_diagnosis()

    plan_b = plan_recovery_action(
        payment=payment_b,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.80,
        diagnosis=diagnosis,
    )

    plan_a = plan_recovery_action(
        payment=payment_a,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.80,
        diagnosis=diagnosis,
    )

    ranked = rank_recovery_candidates(
        [
            (payment_b, plan_b),
            (payment_a, plan_a),
        ]
    )

    assert ranked[0][0].payment_id == "pay_a"
    assert ranked[1][0].payment_id == "pay_b"
