from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)
from app.tools.base import RecoveryTool
from app.integrations.razorpay_client import RazorpayClient
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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


class RazorpayRecoveryLinkTool(RecoveryTool):
    """
    Actual Razorpay API integration to generate a real Payment Link.
    """
    def __init__(self):
        self.client = RazorpayClient()

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
                message="Recovery link tool does not support this recovery action.",
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
            # Use amount from request (now properly carried from the payment record)
            amount = int(request.amount) if request.amount > 0 else 100
            currency = request.currency or "INR"

            link_response = self.client.create_payment_link(
                amount=amount,
                currency=currency,
                description=f"Payment Recovery for {payment_id}",
                reference_id=f"recover_{payment_id}_{int(datetime.now().timestamp())}",
            )

            short_url = link_response.get("short_url")
            link_id = link_response.get("id")

            return ExecutionResult(
                success=True,
                action=action,
                external_reference_id=link_id,
                message=f"Real Payment Link generated successfully: {short_url}",
                metadata={"payment_link_url": short_url, "link_id": link_id},
            )
        except Exception as e:
            logger.error(f"Razorpay API request failed for payment link {payment_id}: {e}")
            return ExecutionResult(
                success=False,
                action=action,
                message=f"Razorpay API error: {str(e)}",
                error_code="EXTERNAL_API_ERROR",
            )