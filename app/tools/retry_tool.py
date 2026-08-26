from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)
from app.tools.base import RecoveryTool
from app.integrations.razorpay_client import RazorpayClient
import logging

logger = logging.getLogger(__name__)


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


class RazorpayRetryTool(RecoveryTool):
    """
    Actual Razorpay API integration for checking payment status or simulating a retry.
    """
    def __init__(self):
        self.client = RazorpayClient()

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
                message="Retry tool does not support this recovery action.",
                error_code="UNSUPPORTED_ACTION",
            )

        if not self.client.client:
            return ExecutionResult(
                success=False,
                action=action,
                message="Razorpay client is not configured.",
                error_code="MISSING_CONFIGURATION",
            )

        try:
            payment_info = self.client.fetch_payment(payment_id)
            status = payment_info.get("status")
            return ExecutionResult(
                success=True,
                action=action,
                external_reference_id=payment_id,
                message=f"Razorpay API called successfully. Current status: {status}",
            )
        except Exception as e:
            logger.error(f"Razorpay API request failed for payment {payment_id}: {e}")
            return ExecutionResult(
                success=False,
                action=action,
                message=f"Razorpay API error: {str(e)}",
                error_code="EXTERNAL_API_ERROR",
            )