from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import RecoveryPlan
from app.workflows.factory import create_recovery_state
from app.workflows.graph import (
    build_recovery_graph,
    execute_node,
)
from app.domain.enums.audit_stage import AuditStage


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


def test_approved_automated_action_executes_successfully() -> None:
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
    assert result["workflow_status"] == "RECOVERY_VERIFIED"

    assert result["execution_result"] is not None
    assert result["execution_result"].success is True

    assert (
        result["execution_result"].action
        == result["recovery_plan"].action
    )
    assert result["verification_result"] is not None

    assert result["verification_result"].verified is True

    assert result["recovered_amount"] == (
    result["recovery_plan"].expected_recovery_value
    )

def test_non_executable_action_has_no_registered_tool() -> None:
    payment = PaymentRiskRecord(
        payment_id="pay_unmapped_001",
        customer_id="cust_004",
        merchant_id="merchant_001",
        amount=5000.0,
        currency="INR",
        payment_method="upi",
        status="failed",
        failure_reason="bank_timeout",
        attempt_count=1,
        event_timestamp="2026-08-25T10:30:00",
        customer_success_rate=0.90,
        previous_retry_success_rate=0.80,
        contact_count=0,
        actual_recovery_outcome=0,
    )

    state = {
        "payment": payment,
        "recovery_plan": RecoveryPlan(
            action=RecoveryAction.DO_NOTHING,
            expected_recovery_value=4000.0,
            priority_score=0.8,
        ),
    }

    result = execute_node(state)

    assert result["workflow_status"] == "EXECUTION_FAILED"

    assert result["execution_result"].success is False

    assert (
        result["execution_result"].action
        == RecoveryAction.DO_NOTHING
    )

    assert (
        result["execution_result"].error_code
        == "TOOL_NOT_REGISTERED"
    )

    assert result["errors"] == [
        "No tool registered for action: do_nothing",
    ]

def test_execution_and_verification_audits_are_accumulated() -> None:
    payment = PaymentRiskRecord(
        payment_id="pay_audit_001",
        customer_id="cust_audit_001",
        merchant_id="merchant_001",
        amount=5000.0,
        currency="INR",
        payment_method="upi",
        status="failed",
        failure_reason="bank_timeout",
        attempt_count=1,
        event_timestamp="2026-08-25T15:00:00",
        customer_success_rate=0.90,
        previous_retry_success_rate=0.80,
        contact_count=0,
        actual_recovery_outcome=1,
    )

    result = run_workflow(payment)

    assert result["workflow_status"] == "RECOVERY_VERIFIED"

    audit_stages = [
        event.stage
        for event in result["audit_trail"]
    ]

    assert AuditStage.EXECUTION in audit_stages
    assert AuditStage.VERIFICATION in audit_stages

    execution_index = audit_stages.index(
        AuditStage.EXECUTION
    )

    verification_index = audit_stages.index(
        AuditStage.VERIFICATION
    )

    assert execution_index < verification_index