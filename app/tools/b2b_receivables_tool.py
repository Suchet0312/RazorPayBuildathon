"""
B2B Receivables Chaser Tool

Handles overdue B2B invoices by escalating through a configurable
reminder → senior-AR → legal sequence with a promise-to-pay capture step.
"""

import logging
from datetime import datetime

from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import ExecutionRequest, ExecutionResult
from app.tools.base import RecoveryTool

logger = logging.getLogger(__name__)

ESCALATION_LEVELS = ["reminder", "senior_ar", "legal"]


class B2BReceivablesChaser(RecoveryTool):
    """
    Chases overdue B2B invoices through structured escalation levels.

    Each invocation advances the case one step along the escalation path.
    In production this would integrate with an AR system (e.g. Zoho Books,
    Tally, SAP). For the prototype it returns the escalation decision.
    """

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if request.action != RecoveryAction.B2B_RECEIVABLES_CHASE:
            return ExecutionResult(
                success=False,
                action=request.action,
                message="B2B receivables tool does not support this action.",
                error_code="UNSUPPORTED_ACTION",
            )

        params = request.action_parameters or {}
        escalation_levels = params.get("escalation_levels", ESCALATION_LEVELS)
        days_overdue = params.get("days_overdue", 0)

        # Select escalation level based on days overdue
        if days_overdue <= 7:
            current_level = escalation_levels[0] if escalation_levels else "reminder"
        elif days_overdue <= 30:
            current_level = escalation_levels[1] if len(escalation_levels) > 1 else "senior_ar"
        else:
            current_level = escalation_levels[-1] if escalation_levels else "legal"

        reference_id = (
            f"b2b_chase_{request.payment_id}_{int(datetime.now().timestamp())}"
        )

        logger.info(
            "B2B chase initiated for payment=%s merchant=%s level=%s days_overdue=%s",
            request.payment_id,
            request.merchant_id,
            current_level,
            days_overdue,
        )

        return ExecutionResult(
            success=True,
            action=request.action,
            external_reference_id=reference_id,
            message=(
                f"B2B receivables chase initiated at escalation level "
                f"'{current_level}' for payment {request.payment_id} "
                f"(amount={request.currency} {request.amount:.2f}, "
                f"days_overdue={days_overdue})."
            ),
            metadata={
                "escalation_level": current_level,
                "days_overdue": days_overdue,
                "amount": request.amount,
                "currency": request.currency,
                "merchant_id": request.merchant_id,
                "customer_id": request.customer_id,
                "initiated_at": datetime.utcnow().isoformat(),
                "reference_id": reference_id,
            },
        )
