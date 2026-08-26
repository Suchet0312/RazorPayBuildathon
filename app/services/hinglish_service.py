"""
Hinglish Voice Recovery Service

Generates a Hinglish recovery message and simulates dispatch via
SMS / voice / WhatsApp. Uses the tool layer so the same templates
and logic stay consistent with the workflow execution path.
"""

from __future__ import annotations

import logging
from datetime import datetime

from app.api.schemas.requests import HinglishRecoveryRequest
from app.api.schemas.responses import HinglishRecoveryResponse
from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import ExecutionRequest
from app.tools.hinglish_voice_tool import HinglishVoiceRecoveryTool

logger = logging.getLogger(__name__)


class HinglishService:
    def __init__(self) -> None:
        self._tool = HinglishVoiceRecoveryTool()

    def dispatch(self, request: HinglishRecoveryRequest) -> HinglishRecoveryResponse:
        exec_request = ExecutionRequest(
            run_id=f"hinglish_{request.payment_id}_{int(datetime.now().timestamp())}",
            payment_id=request.payment_id,
            action=RecoveryAction.HINGLISH_VOICE_RECOVERY,
            action_parameters={
                "failure_hint": (request.failure_reason or "default").lower(),
                "channel": request.channel,
            },
            amount=request.amount,
            currency=request.currency,
            customer_id=request.customer_id,
            merchant_id=request.merchant_id,
        )

        result = self._tool.execute(exec_request)

        if not result.success:
            raise RuntimeError(result.message)

        meta = result.metadata or {}
        return HinglishRecoveryResponse(
            reference_id=result.external_reference_id or "",
            payment_id=request.payment_id,
            channel=request.channel,
            message_sent=meta.get("message", ""),
            dispatched_at=meta.get("dispatched_at", datetime.utcnow().isoformat()),
            metadata=meta,
        )
