"""
Promise-to-Pay Tracker Tool

Captures a customer's payment commitment and schedules automated
follow-ups to confirm fulfilment within the agreed window.
"""

import logging
from datetime import datetime, timedelta

from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import ExecutionRequest, ExecutionResult
from app.tools.base import RecoveryTool

logger = logging.getLogger(__name__)


class PromiseToPayTool(RecoveryTool):
    """
    Records a promise-to-pay commitment and schedules follow-up nudges.

    In production this stores the commitment in a CRM / collections DB
    and enqueues follow-up notifications. For the prototype it returns
    the commitment details with a reference ID.
    """

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if request.action != RecoveryAction.PROMISE_TO_PAY:
            return ExecutionResult(
                success=False,
                action=request.action,
                message="Promise-to-pay tool does not support this action.",
                error_code="UNSUPPORTED_ACTION",
            )

        params = request.action_parameters or {}
        commitment_window_days = params.get("commitment_window_days", 3)
        follow_up_enabled = params.get("follow_up_enabled", True)

        now = datetime.utcnow()
        commitment_deadline = now + timedelta(days=commitment_window_days)
        follow_up_times = []
        if follow_up_enabled:
            # Follow-up at 50% and 90% of the commitment window
            follow_up_times = [
                (now + timedelta(days=commitment_window_days * 0.5)).isoformat(),
                (now + timedelta(days=commitment_window_days * 0.9)).isoformat(),
            ]

        reference_id = (
            f"ptp_{request.payment_id}_{int(now.timestamp())}"
        )

        logger.info(
            "Promise-to-pay captured for payment=%s customer=%s deadline=%s",
            request.payment_id,
            request.customer_id,
            commitment_deadline.isoformat(),
        )

        return ExecutionResult(
            success=True,
            action=request.action,
            external_reference_id=reference_id,
            message=(
                f"Promise-to-pay commitment recorded for payment "
                f"{request.payment_id}. Customer must pay by "
                f"{commitment_deadline.strftime('%Y-%m-%d')}."
            ),
            metadata={
                "commitment_deadline": commitment_deadline.isoformat(),
                "commitment_window_days": commitment_window_days,
                "follow_up_times": follow_up_times,
                "customer_id": request.customer_id,
                "amount": request.amount,
                "currency": request.currency,
                "reference_id": reference_id,
                "captured_at": now.isoformat(),
            },
        )
