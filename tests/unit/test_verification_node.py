from app.domain.enums.audit_stage import AuditStage
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import (
    ExecutionResult,
    RecoveryPlan,
)
from app.workflows.verification import verify_node


def make_state() -> dict:
    return {
        "run_id": "run_verify_001",
        "payment": PaymentRiskRecord(
            payment_id="pay_verify_001",
            customer_id="cust_verify_001",
            merchant_id="merchant_001",
            amount=5000.0,
            currency="INR",
            payment_method="upi",
            status="failed",
            failure_reason="bank_timeout",
            attempt_count=1,
            event_timestamp="2026-08-25T14:00:00",
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


def test_successful_execution_is_verified() -> None:
    state = make_state()

    state["execution_result"] = ExecutionResult(
        success=True,
        action=RecoveryAction.RETRY_NOW,
        external_reference_id="retry_001",
        message="Retry completed successfully.",
    )

    result = verify_node(state)

    assert result["workflow_status"] == "RECOVERY_VERIFIED"

    assert result["verification_result"].verified is True

    assert result["recovered_amount"] == 4000.0


def test_failed_execution_is_not_verified() -> None:
    state = make_state()

    state["execution_result"] = ExecutionResult(
        success=False,
        action=RecoveryAction.RETRY_NOW,
        message="Retry failed.",
        error_code="RETRY_FAILED",
    )

    result = verify_node(state)

    assert result["workflow_status"] == "RECOVERY_NOT_VERIFIED"

    assert result["verification_result"].verified is False

    assert result["recovered_amount"] == 0.0


def test_successful_verification_creates_audit_event() -> None:
    state = make_state()

    state["execution_result"] = ExecutionResult(
        success=True,
        action=RecoveryAction.RETRY_NOW,
        external_reference_id="retry_001",
        message="Retry completed successfully.",
    )

    result = verify_node(state)

    audit_event = result["audit_trail"][0]

    assert audit_event.run_id == "run_verify_001"

    assert audit_event.payment_id == (
        state["payment"].payment_id
    )

    assert audit_event.stage == AuditStage.VERIFICATION

    assert audit_event.actor == "verify_node"

    assert audit_event.decision == "recovery_verified"

    assert audit_event.result == "success"

    assert audit_event.metadata["recovered_amount"] == 4000.0


def test_failed_verification_creates_failure_audit_event() -> None:
    state = make_state()

    state["execution_result"] = ExecutionResult(
        success=False,
        action=RecoveryAction.RETRY_NOW,
        message="Retry failed.",
        error_code="RETRY_FAILED",
    )

    result = verify_node(state)

    audit_event = result["audit_trail"][0]

    assert audit_event.stage == AuditStage.VERIFICATION

    assert audit_event.decision == (
        "recovery_not_verified"
    )

    assert audit_event.result == "failed"

    assert audit_event.reason_codes == [
        "RECOVERY_NOT_VERIFIED",
    ]

    assert audit_event.metadata["recovered_amount"] == 0.0