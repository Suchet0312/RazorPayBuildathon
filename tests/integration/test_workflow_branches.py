from app.domain.models.payment import PaymentRiskRecord
from app.workflows.factory import create_recovery_state
from app.workflows.graph import build_recovery_graph


def run_workflow(payment: PaymentRiskRecord) -> dict:
    graph = build_recovery_graph()

    initial_state = create_recovery_state(
        run_id=f"run_{payment.payment_id}",
        payment=payment,
    )

    return graph.invoke(initial_state)


def test_permanent_failure_routes_to_no_action() -> None:
    payment = PaymentRiskRecord(
        payment_id="pay_permanent_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        amount=5000.0,
        currency="INR",
        payment_method="upi",
        status="failed",
        failure_reason="invalid_details",
        attempt_count=1,
        event_timestamp="2026-08-24T10:30:00",
        customer_success_rate=0.90,
        previous_retry_success_rate=0.80,
        contact_count=0,
        actual_recovery_outcome=0,
    )

    result = run_workflow(payment)

    assert result["policy_approved"] is True
    assert result["workflow_status"] == "NO_ACTION_REQUIRED"


def test_amount_limit_routes_to_policy_blocked() -> None:
    payment = PaymentRiskRecord(
        payment_id="pay_blocked_001",
        customer_id="cust_002",
        merchant_id="merchant_001",
        amount=15000.0,
        currency="INR",
        payment_method="upi",
        status="failed",
        failure_reason="bank_timeout",
        attempt_count=1,
        event_timestamp="2026-08-24T10:30:00",
        customer_success_rate=0.90,
        previous_retry_success_rate=0.80,
        contact_count=0,
        actual_recovery_outcome=0,
    )

    result = run_workflow(payment)

    assert result["policy_approved"] is False
    assert result["workflow_status"] == "POLICY_BLOCKED"


def test_approved_automated_action_routes_to_execution_ready() -> None:
    payment = PaymentRiskRecord(
        payment_id="pay_execute_001",
        customer_id="cust_003",
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

    result = run_workflow(payment)

    assert result["policy_approved"] is True
    assert result["workflow_status"] == "EXECUTION_READY"