from app.domain.enums.audit_stage import AuditStage
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import (
    ExecutionResult,
    RecoveryPlan,
)
from app.workflows.factory import create_recovery_state
from app.workflows.verification import verify_node


def make_state() -> dict:
    payment = PaymentRiskRecord(
        payment_id="pay_verification_audit_001",
        customer_id="cust_001",
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
        actual_recovery_outcome=1,
    )

    state = create_recovery_state(
        run_id="run_verification_audit_001",
        payment=payment,
    )

    state["recovery_plan"] = RecoveryPlan(
        action=RecoveryAction.RETRY_NOW,
        expected_recovery_value=4000.0,
        priority_score=0.8,
    )

    return state


def test_successful_verification_creates_audit_event() -> None:
    state = make_state()

    state["execution_result"] = ExecutionResult(
        success=True,
        action=RecoveryAction.RETRY_NOW,
        external_reference_id="mock_retry_001",
        message="Execution succeeded.",
    )

    result = verify_node(state)

    assert result["workflow_status"] == "RECOVERY_VERIFIED"

    assert len(result["audit_trail"]) == 1

    audit_event = result["audit_trail"][0]

    assert audit_event.stage == AuditStage.VERIFICATION
    assert audit_event.decision == "recovery_verified"
    assert audit_event.result == "success"
    assert audit_event.reason_codes == []

    assert audit_event.metadata["recovered_amount"] == 4000.0


def test_failed_verification_creates_audit_event() -> None:
    state = make_state()

    state["execution_result"] = ExecutionResult(
        success=False,
        action=RecoveryAction.RETRY_NOW,
        message="Execution failed.",
        error_code="TOOL_EXECUTION_ERROR",
    )

    result = verify_node(state)

    assert result["workflow_status"] == "RECOVERY_NOT_VERIFIED"

    assert len(result["audit_trail"]) == 1

    audit_event = result["audit_trail"][0]

    assert audit_event.stage == AuditStage.VERIFICATION
    assert audit_event.decision == "recovery_not_verified"
    assert audit_event.result == "failed"

    assert audit_event.reason_codes == [
        "RECOVERY_NOT_VERIFIED",
    ]

    assert audit_event.metadata["recovered_amount"] == 0.0