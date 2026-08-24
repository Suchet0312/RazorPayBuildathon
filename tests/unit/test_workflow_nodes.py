from app.domain.models.payment import PaymentRiskRecord
from app.workflows.factory import create_recovery_state
from app.workflows.nodes import (
    classify_node,
    diagnosis_node,
    planning_node,
    policy_node,
    predict_node,
)


def build_test_payment() -> PaymentRiskRecord:
    return PaymentRiskRecord(
        payment_id="pay_workflow_001",
        customer_id="cust_workflow_001",
        merchant_id="merchant_001",
        amount=5000.0,
        currency="INR",
        payment_method="upi",
        status="failed",
        failure_reason="bank_timeout",
        attempt_count=1,
        event_timestamp="2026-08-24T10:30:00",
        customer_success_rate=0.90,
        previous_retry_success_rate=0.80,
        contact_count=0,
        actual_recovery_outcome=1,
    )


def test_classify_node() -> None:
    payment = build_test_payment()

    state = create_recovery_state(
        run_id="run_workflow_001",
        payment=payment,
    )

    result = classify_node(state)

    assert result["classification"] == "temporary_failure"
    assert result["failure_category"].value == "temporary_failure"


def test_predict_node() -> None:
    payment = build_test_payment()

    state = create_recovery_state(
        run_id="run_workflow_001",
        payment=payment,
    )

    result = predict_node(state)

    assert 0.0 <= result["recovery_probability"] <= 1.0


def test_diagnosis_node() -> None:
    payment = build_test_payment()

    state = create_recovery_state(
        run_id="run_workflow_001",
        payment=payment,
    )

    state.update(
        classify_node(state)
    )

    state.update(
        predict_node(state)
    )

    result = diagnosis_node(state)

    assert result["diagnosis"].reason_codes
    assert 0.0 <= result["diagnosis"].confidence <= 1.0


def test_planning_node() -> None:
    payment = build_test_payment()

    state = create_recovery_state(
        run_id="run_workflow_001",
        payment=payment,
    )

    state.update(
        classify_node(state)
    )

    state.update(
        predict_node(state)
    )

    state.update(
        diagnosis_node(state)
    )

    result = planning_node(state)

    assert result["recovery_plan"] is not None
    assert result["expected_recovery_value"] >= 0.0
    assert result["priority_score"] >= 0.0


def test_policy_node() -> None:
    payment = build_test_payment()

    state = create_recovery_state(
        run_id="run_workflow_001",
        payment=payment,
    )

    state.update(
        classify_node(state)
    )

    state.update(
        predict_node(state)
    )

    state.update(
        diagnosis_node(state)
    )

    state.update(
        planning_node(state)
    )

    result = policy_node(state)

    assert result["policy_decision"] is not None
    assert result["policy_approved"] == (
        result["policy_decision"].approved
    )