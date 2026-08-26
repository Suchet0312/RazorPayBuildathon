"""
Hinglish Voice Recovery Tool

Generates a Hinglish (Hindi + English code-switch) recovery message
and simulates dispatching it as a voice/SMS nudge to the customer.

In production this would call a TTS provider (e.g. Sarvam AI, Google TTS)
and route through an IVR or WhatsApp Business API.
"""

import logging
from datetime import datetime

from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import ExecutionRequest, ExecutionResult
from app.tools.base import RecoveryTool

logger = logging.getLogger(__name__)

# Template library — indexed by failure hint found in action_parameters
HINGLISH_TEMPLATES = {
    "insufficient_funds": (
        "Namaste! Aapka payment {amount} {currency} fail ho gaya hai "
        "kyunki account mein sufficient funds nahi the. "
        "Please apne account ko top-up karein aur yahan click karein: {link}"
    ),
    "authentication_failed": (
        "Hello! Aapka {amount} {currency} ka payment authenticate nahi hua. "
        "Apna OTP ya UPI PIN dobara check karein aur retry karein: {link}"
    ),
    "mandate_rejected": (
        "Namaste! Aapki recurring payment {amount} {currency} process nahi hui. "
        "Apna mandate update karne ke liye yahan jaayein: {link}"
    ),
    "default": (
        "Hello! Aapka {amount} {currency} ka payment complete nahi hua. "
        "Dobara try karne ke liye yahan click karein: {link}"
    ),
}


def _build_message(
    failure_hint: str,
    amount: float,
    currency: str,
    payment_id: str,
) -> str:
    template = HINGLISH_TEMPLATES.get(failure_hint, HINGLISH_TEMPLATES["default"])
    link = f"https://pay.razorpay.com/recover/{payment_id}"
    return template.format(amount=f"{amount:.2f}", currency=currency, link=link)


class HinglishVoiceRecoveryTool(RecoveryTool):
    """
    Sends a Hinglish recovery nudge (voice/SMS) to the customer.
    """

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if request.action != RecoveryAction.HINGLISH_VOICE_RECOVERY:
            return ExecutionResult(
                success=False,
                action=request.action,
                message="Hinglish voice tool does not support this action.",
                error_code="UNSUPPORTED_ACTION",
            )

        params = request.action_parameters or {}
        failure_hint = params.get("failure_hint", "default")
        channel = params.get("channel", "sms")  # sms | voice | whatsapp

        message = _build_message(
            failure_hint=failure_hint,
            amount=request.amount,
            currency=request.currency,
            payment_id=request.payment_id,
        )

        reference_id = (
            f"hinglish_{channel}_{request.payment_id}_"
            f"{int(datetime.now().timestamp())}"
        )

        logger.info(
            "Hinglish recovery %s sent for payment=%s customer=%s",
            channel,
            request.payment_id,
            request.customer_id,
        )

        return ExecutionResult(
            success=True,
            action=request.action,
            external_reference_id=reference_id,
            message=f"Hinglish {channel} recovery message dispatched for {request.payment_id}.",
            metadata={
                "channel": channel,
                "message": message,
                "customer_id": request.customer_id,
                "dispatched_at": datetime.utcnow().isoformat(),
                "reference_id": reference_id,
            },
        )
