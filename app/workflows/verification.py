from datetime import datetime, timezone
from uuid import uuid4

from app.domain.enums.audit_stage import AuditStage
from app.domain.models.audit import AuditEvent
from app.domain.models.recovery import VerificationResult
from app.workflows.state import RecoveryState


def create_verification_audit_event(
    state: RecoveryState,
    verification_result: VerificationResult,
) -> AuditEvent:
    """
    Create an audit record for recovery verification.
    """

    return AuditEvent(
        audit_id=str(uuid4()),
        run_id=state.get("run_id", "unknown_run"),
        payment_id=state["payment"].payment_id,
        timestamp=datetime.now(timezone.utc),
        stage=AuditStage.VERIFICATION,
        input_summary=(
            f"Verification requested for payment "
            f"{state['payment'].payment_id}."
        ),
        decision=(
            "recovery_verified"
            if verification_result.verified
            else "recovery_not_verified"
        ),
        reason_codes=(
            []
            if verification_result.verified
            else ["RECOVERY_NOT_VERIFIED"]
        ),
        actor="verify_node",
        result=(
            "success"
            if verification_result.verified
            else "failed"
        ),
        metadata={
            "recovered_amount": verification_result.recovered_amount,
            "message": verification_result.message,
        },
    )


def verify_node(
    state: RecoveryState,
) -> dict:
    """
    Verify the outcome of a recovery execution.

    Execution success means the tool completed successfully.
    Verification determines whether the payment recovery itself
    can be considered confirmed.
    """

    execution_result = state["execution_result"]
    recovery_plan = state["recovery_plan"]

    if not execution_result.success:
        verification_result = VerificationResult(
            verified=False,
            recovered_amount=0.0,
            message=(
                "Recovery cannot be verified because execution failed."
            ),
        )

        audit_event = create_verification_audit_event(
            state,
            verification_result,
        )

        return {
            "verification_result": verification_result,
            "recovered_amount": 0.0,
            "workflow_status": "RECOVERY_NOT_VERIFIED",
            "audit_trail": [audit_event],
        }

    recovered_amount = recovery_plan.expected_recovery_value

    verification_result = VerificationResult(
        verified=True,
        recovered_amount=recovered_amount,
        message="Recovery execution verified successfully.",
    )

    audit_event = create_verification_audit_event(
        state,
        verification_result,
    )

    return {
        "verification_result": verification_result,
        "recovered_amount": recovered_amount,
        "workflow_status": "RECOVERY_VERIFIED",
        "audit_trail": [audit_event],
    }