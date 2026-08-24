from app.domain.models.payment import PaymentRiskRecord
from app.workflows.factory import create_recovery_state
from app.workflows.graph import build_recovery_graph


def build_test_payment() -> PaymentRiskRecord:
    return PaymentRiskRecord(
        payment_id="pay_graph_001",
        customer_id="cust_graph_001",
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


def test_recovery_graph_runs_end_to_end() -> None:
    graph = build_recovery_graph()

    payment = build_test_payment()

    initial_state = create_recovery_state(
        run_id="run_graph_001",
        payment=payment,
    )

    result = graph.invoke(initial_state)

    assert result["classification"] == "temporary_failure"

    assert (
        0.0
        <= result["recovery_probability"]
        <= 1.0
    )

    assert result["diagnosis"] is not None
    assert result["recovery_plan"] is not None
    assert result["policy_decision"] is not None

    assert result["policy_approved"] == (
        result["policy_decision"].approved
    )
    assert result["workflow_status"] in {
    "RECOVERY_VERIFIED",
    "RECOVERY_NOT_VERIFIED",
    "POLICY_BLOCKED",
    "NO_ACTION_REQUIRED",
    "MERCHANT_ESCALATION_REQUIRED",
}