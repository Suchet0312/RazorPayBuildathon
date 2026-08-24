from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)
from app.tools.base import RecoveryTool


class MockRetryTool(RecoveryTool):
    """
    Deterministic mock execution tool for payment retry actions.

    This tool provides execution capability only.
    It does not evaluate policy or decide whether execution is allowed.
    """

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        action = request.action
        payment_id = request.payment_id

        if action not in {
            RecoveryAction.RETRY_NOW,
            RecoveryAction.RETRY_LATER,
        }:
            return ExecutionResult(
                success=False,
                action=action,
                message=(
                    "Retry tool does not support this recovery action."
                ),
                error_code="UNSUPPORTED_ACTION",
            )

        return ExecutionResult(
            success=True,
            action=action,
            external_reference_id=f"mock_retry_{payment_id}",
            message="Mock payment retry executed successfully.",
        )