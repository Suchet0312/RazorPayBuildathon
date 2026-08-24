from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)
from app.tools.base import RecoveryTool


class MockRecoveryLinkTool(RecoveryTool):
    """
    Deterministic mock tool for sending a payment recovery link.

    This tool provides execution capability only.
    It does not evaluate policy or decide whether execution is allowed.
    """

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        action = request.action
        payment_id = request.payment_id

        if action != RecoveryAction.SEND_RECOVERY_LINK:
            return ExecutionResult(
                success=False,
                action=action,
                message=(
                    "Recovery link tool does not support "
                    "this recovery action."
                ),
                error_code="UNSUPPORTED_ACTION",
            )

        return ExecutionResult(
            success=True,
            action=action,
            external_reference_id=(
                f"mock_recovery_link_{payment_id}"
            ),
            message="Mock recovery link sent successfully.",
        )