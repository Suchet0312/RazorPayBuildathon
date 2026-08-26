"""
Promise-to-Pay Service

Captures payment commitments and schedules follow-up nudges.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from app.api.schemas.requests import PromiseToPayRequest
from app.api.schemas.responses import PromiseToPayResponse

logger = logging.getLogger(__name__)


class PromiseToPayService:
    """
    Records a customer's payment commitment and returns a structured
    response with the deadline and follow-up schedule.

    In production this would persist to a CRM / collections table and
    enqueue follow-up jobs. For the prototype the logic is in-memory.
    """

    def record_commitment(self, request: PromiseToPayRequest) -> PromiseToPayResponse:
        now = datetime.utcnow()
        deadline = now + timedelta(days=request.commitment_window_days)

        follow_up_times: list[str] = []
        if request.follow_up_enabled:
            follow_up_times = [
                (now + timedelta(days=request.commitment_window_days * 0.5)).isoformat(),
                (now + timedelta(days=request.commitment_window_days * 0.9)).isoformat(),
            ]

        reference_id = f"ptp_{request.payment_id}_{int(now.timestamp())}"

        logger.info(
            "Promise-to-pay recorded: payment=%s customer=%s deadline=%s",
            request.payment_id,
            request.customer_id,
            deadline.date(),
        )

        return PromiseToPayResponse(
            reference_id=reference_id,
            payment_id=request.payment_id,
            customer_id=request.customer_id,
            commitment_deadline=deadline.isoformat(),
            follow_up_times=follow_up_times,
            message=(
                f"Payment commitment of {request.currency} {request.amount:.2f} "
                f"recorded. Customer must pay by {deadline.strftime('%Y-%m-%d')}."
            ),
            metadata={
                "commitment_window_days": request.commitment_window_days,
                "follow_up_enabled": request.follow_up_enabled,
                "notes": request.notes,
                "captured_at": now.isoformat(),
                "merchant_id": request.merchant_id,
                "amount": request.amount,
                "currency": request.currency,
            },
        )
