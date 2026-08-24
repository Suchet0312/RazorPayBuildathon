from app.domain.enums.audit_stage import AuditStage
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import RecoveryPlan
from app.workflows.graph import execute_node


def make_state() -> dict:
    return {
        "run_id": "run_audit_001",
        "payment": PaymentRiskRecord(
            payment_id="pay_audit_001",
            customer_id="cust_audit_001",
            merchant_id="merchant_001",
            amount=5000.0,
            currency="INR",
            payment_method="upi",
            status="failed",
            failure_reason="bank_timeout",
            attempt_count=1,
            event_timestamp="2026-08-25T13:00:00",
            customer_success_rate=0.90,
            previous_retry_success_rate=0.80,
            contact_count=0,
            actual_recovery_outcome=1,
        ),
        "recovery_plan": RecoveryPlan(
            action=RecoveryAction.RETRY_NOW,
            expected_recovery_value=4000.0,
            priority_score=0.8,
        ),
    }


def test_successful_execution_creates_audit_event() -> None:
    result = execute_node(
        make_state(),
    )

    assert result["workflow_status"] == "EXECUTION_SUCCEEDED"

    assert "audit_trail" in result

    assert len(result["audit_trail"]) == 1

    audit_event = result["audit_trail"][0]

    assert audit_event.run_id == "run_audit_001"

    assert audit_event.payment_id == "pay_audit_001"

    assert audit_event.stage == AuditStage.EXECUTION

    assert audit_event.actor == "execute_node"

    assert audit_event.decision == (
        "tool_execution_succeeded"
    )

    assert audit_event.result == "success"

    assert audit_event.metadata["external_reference_id"] is not None


def test_unregistered_tool_creates_failure_audit_event() -> None:
    state = make_state()

    state["recovery_plan"] = RecoveryPlan(
        action=RecoveryAction.DO_NOTHING,
        expected_recovery_value=0.0,
        priority_score=0.0,
    )

    result = execute_node(
        state,
    )

    assert result["workflow_status"] == "EXECUTION_FAILED"

    assert len(result["audit_trail"]) == 1

    audit_event = result["audit_trail"][0]

    assert audit_event.stage == AuditStage.EXECUTION

    assert audit_event.decision == "tool_not_registered"

    assert audit_event.result == "failed"

    assert audit_event.reason_codes == [
        "TOOL_NOT_REGISTERED",
    ]

    assert (
        audit_event.metadata["error_code"]
        == "TOOL_NOT_REGISTERED"
    )