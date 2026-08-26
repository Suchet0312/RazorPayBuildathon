"""
MCP tool definitions for the Recovery Brain.

Each function here is exposed as a callable MCP tool that an AI agent
(or any MCP client) can invoke to interact with the recovery system.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lazy imports – avoid circular imports at module load time
# ---------------------------------------------------------------------------

def _get_recovery_service():
    from app.services.recovery_service import RecoveryService
    return RecoveryService()


def _get_dashboard_service():
    from app.services.dashboard_service import DashboardService
    return DashboardService()


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def analyze_payment(
    payment_id: str,
    customer_id: str,
    merchant_id: str,
    amount: float,
    currency: str,
    payment_method: str,
    status: str,
    event_timestamp: str,
    customer_success_rate: float,
    previous_retry_success_rate: float,
    failure_reason: str | None = None,
    attempt_count: int = 0,
    contact_count: int = 0,
) -> dict[str, Any]:
    """
    Run the full AI recovery workflow for a single payment.

    Returns the complete workflow result including classification,
    ML probability, recovery plan, policy decision, and execution result.
    """
    from app.api.schemas.requests import RecoveryAnalyzeRequest
    from app.domain.enums.payment_status import PaymentStatus

    try:
        request = RecoveryAnalyzeRequest(
            payment_id=payment_id,
            customer_id=customer_id,
            merchant_id=merchant_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            status=PaymentStatus(status),
            failure_reason=failure_reason,
            attempt_count=attempt_count,
            event_timestamp=datetime.fromisoformat(event_timestamp),
            customer_success_rate=customer_success_rate,
            previous_retry_success_rate=previous_retry_success_rate,
            contact_count=contact_count,
        )
        svc = _get_recovery_service()
        result = svc.analyze_payment(request)
        return result.model_dump()
    except Exception as exc:
        logger.error("MCP analyze_payment failed: %s", exc, exc_info=True)
        return {"error": str(exc)}


def get_recovery_status(run_id: str) -> dict[str, Any]:
    """
    Get the current status and full audit trail for a recovery run.
    """
    try:
        svc = _get_recovery_service()
        result = svc.get_status(run_id)
        if result is None:
            return {"error": f"Run '{run_id}' not found"}
        return result
    except Exception as exc:
        logger.error("MCP get_recovery_status failed: %s", exc, exc_info=True)
        return {"error": str(exc)}


def get_dashboard_metrics() -> dict[str, Any]:
    """
    Return aggregated revenue recovery metrics across all processed payments.
    """
    try:
        svc = _get_dashboard_service()
        result = svc.get_metrics()
        return result.model_dump()
    except Exception as exc:
        logger.error("MCP get_dashboard_metrics failed: %s", exc, exc_info=True)
        return {"error": str(exc)}


def list_recovery_batches() -> list[dict[str, Any]]:
    """
    List all recovery workflow runs ordered by most recent first.
    """
    try:
        svc = _get_dashboard_service()
        batches = svc.get_batches()
        return [b.model_dump() for b in batches]
    except Exception as exc:
        logger.error("MCP list_recovery_batches failed: %s", exc, exc_info=True)
        return [{"error": str(exc)}]


def get_payment_details(run_id: str) -> dict[str, Any]:
    """
    Get the full drill-down for a specific recovery run including audit trail.
    """
    try:
        svc = _get_dashboard_service()
        result = svc.get_payment_details(run_id)
        if result is None:
            return {"error": f"Run '{run_id}' not found"}
        return result.model_dump()
    except Exception as exc:
        logger.error("MCP get_payment_details failed: %s", exc, exc_info=True)
        return {"error": str(exc)}


def classify_failure_reason(failure_reason: str) -> dict[str, Any]:
    """
    Classify a payment failure reason into its failure category.
    Useful for quick triage without running the full workflow.
    """
    try:
        from app.intelligence.classification.rules import classify_failure
        category = classify_failure(failure_reason)
        return {
            "failure_reason": failure_reason,
            "failure_category": category.value,
        }
    except Exception as exc:
        return {"error": str(exc)}


def predict_recovery_chance(
    amount: float,
    payment_method: str,
    failure_reason: str,
    attempt_count: int,
    customer_success_rate: float,
    previous_retry_success_rate: float,
    hour_of_day: int = 12,
    day_of_week: int = 0,
) -> dict[str, Any]:
    """
    Run only the ML prediction step to get a recovery probability estimate.
    """
    try:
        import pandas as pd
        from app.intelligence.features.feature_builder import build_features
        from app.intelligence.models.predict import load_model, predict_recovery_probability
        from app.intelligence.classification.rules import classify_failure

        failure_category = classify_failure(failure_reason).value

        df = pd.DataFrame([{
            "amount": amount,
            "payment_method": payment_method,
            "failure_reason": failure_reason,
            "failure_category": failure_category,
            "attempt_count": attempt_count,
            "customer_success_rate": customer_success_rate,
            "previous_retry_success_rate": previous_retry_success_rate,
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
        }])

        features, _ = build_features(df)
        model = load_model()
        probability = predict_recovery_probability(model=model, features=features)

        return {
            "failure_reason": failure_reason,
            "failure_category": failure_category,
            "recovery_probability": round(probability, 4),
            "recoverable": probability >= 0.55,
        }
    except Exception as exc:
        logger.error("MCP predict_recovery_chance failed: %s", exc, exc_info=True)
        return {"error": str(exc)}
