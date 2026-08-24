from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)
from app.tools.base import RecoveryTool


class MockAlternateMethodTool(RecoveryTool):
    """
    Deterministic mock tool for suggesting an alternate payment method.

    This tool provides execution capability only.
    It does not evaluate policy or decide whether execution is allowed.
    """

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        action = request.action
        payment_id = request.payment_id

        if action != RecoveryAction.SUGGEST_ALTERNATE_METHOD:
            return ExecutionResult(
                success=False,
                action=action,
                message=(
                    "Alternate method tool does not support "
                    "this recovery action."
                ),
                error_code="UNSUPPORTED_ACTION",
            )

        return ExecutionResult(
            success=True,
            action=action,
            external_reference_id=(
                f"mock_alternate_method_{payment_id}"
            ),
            message=(
                "Mock alternate payment method suggestion "
                "generated successfully."
            ),
        )