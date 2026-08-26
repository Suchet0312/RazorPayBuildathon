"""
Mandate Retry Sequencer Tool

Handles NACH / ECS / UPI AutoPay mandate retries and recurring
subscription payment failures using a timed retry sequence.
"""

import logging
from datetime import datetime

from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import ExecutionRequest, ExecutionResult
from app.tools.base import RecoveryTool

logger = logging.getLogger(__name__)

# Default retry cadence: 1 h, 24 h, 72 h after the first attempt
DEFAULT_RETRY_SEQUENCE = ["T+1h", "T+24h", "T+72h"]


class MandateRetryTool(RecoveryTool):
    """
    Sequences a timed retry for mandate / subscription payment failures.

    In production this would enqueue jobs in a task queue (Celery / BullMQ).
    For the prototype it returns a sequenced retry plan with a reference ID.
    """

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if request.action != RecoveryAction.MANDATE_RETRY:
            return ExecutionResult(
                success=False,
                action=request.action,
                message="Mandate retry tool does not support this action.",
                error_code="UNSUPPORTED_ACTION",
            )

        params = request.action_parameters or {}
        retry_sequence = params.get("retry_sequence", DEFAULT_RETRY_SEQUENCE)
        notify_customer = params.get("notify_customer", True)

        reference_id = (
            f"mandate_retry_{request.payment_id}_{int(datetime.now().timestamp())}"
        )

        logger.info(
            "Mandate retry sequenced for payment=%s sequence=%s notify=%s",
            request.payment_id,
            retry_sequence,
            notify_customer,
        )

        return ExecutionResult(
            success=True,
            action=request.action,
            external_reference_id=reference_id,
            message=(
                f"Mandate retry sequence {retry_sequence} scheduled "
                f"for payment {request.payment_id}."
            ),
            metadata={
                "retry_sequence": retry_sequence,
                "notify_customer": notify_customer,
                "scheduled_at": datetime.utcnow().isoformat(),
                "reference_id": reference_id,
            },
        )
