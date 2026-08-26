"""
Recovery Brain MCP Server

Exposes recovery tools over the Model Context Protocol so any MCP-compatible
AI agent (Claude, GPT-4o, Kiro, etc.) can directly invoke recovery operations.

Usage (standalone):
    python -m app.mcp.server

Usage (mounted inside FastAPI — see app/main.py):
    from app.mcp.server import create_mcp_app
    app.mount("/mcp", create_mcp_app())
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Try to import the MCP SDK; degrade gracefully if not installed.
# ---------------------------------------------------------------------------
try:
    from mcp.server.fastmcp import FastMCP
    _MCP_AVAILABLE = True
except ImportError:  # pragma: no cover
    FastMCP = None  # type: ignore[assignment,misc]
    _MCP_AVAILABLE = False
    logger.warning(
        "mcp[cli] package not installed — MCP server will be unavailable. "
        "Install it with: pip install 'mcp[cli]'"
    )

from app.mcp.tools import (
    analyze_payment,
    classify_failure_reason,
    get_dashboard_metrics,
    get_payment_details,
    get_recovery_status,
    list_recovery_batches,
    predict_recovery_chance,
)


def create_mcp_app() -> Any:
    """
    Build and return the FastMCP ASGI application.

    Returns None if the MCP SDK is not installed.
    """
    if not _MCP_AVAILABLE:
        logger.error("Cannot create MCP app — mcp[cli] not installed.")
        return None

    mcp = FastMCP(
        name="Recovery Brain",
        instructions=(
            "You are connected to the Razorpay Recovery Brain. "
            "Use these tools to detect revenue at risk, diagnose payment "
            "failures, and execute bounded recovery actions with full audit trails."
        ),
    )

    # ------------------------------------------------------------------
    # Register tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def run_recovery_workflow(
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
        Run the full AI recovery pipeline for a payment.

        Classifies the failure, predicts recovery probability via ML,
        diagnoses the root cause, selects a bounded recovery action,
        enforces policy controls, and executes the approved action.
        Returns the complete result with audit trail.
        """
        return analyze_payment(
            payment_id=payment_id,
            customer_id=customer_id,
            merchant_id=merchant_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            status=status,
            event_timestamp=event_timestamp,
            customer_success_rate=customer_success_rate,
            previous_retry_success_rate=previous_retry_success_rate,
            failure_reason=failure_reason,
            attempt_count=attempt_count,
            contact_count=contact_count,
        )

    @mcp.tool()
    def check_recovery_status(run_id: str) -> dict[str, Any]:
        """
        Check the status and audit trail of a recovery workflow run.
        """
        return get_recovery_status(run_id)

    @mcp.tool()
    def fetch_dashboard_metrics() -> dict[str, Any]:
        """
        Get aggregated revenue recovery metrics: total processed,
        revenue at risk, predicted recoverable, actually recovered,
        recovery rate, approved/blocked action counts.
        """
        return get_dashboard_metrics()

    @mcp.tool()
    def fetch_recovery_batches() -> list[dict[str, Any]]:
        """
        List all recovery workflow runs with summary details,
        ordered by most recent first.
        """
        return list_recovery_batches()

    @mcp.tool()
    def fetch_payment_details(run_id: str) -> dict[str, Any]:
        """
        Get the full drill-down for a recovery run including the
        intelligence layer output, diagnosis, plan, policy decision,
        execution result, and complete audit trail.
        """
        return get_payment_details(run_id)

    @mcp.tool()
    def triage_failure(failure_reason: str) -> dict[str, Any]:
        """
        Quickly classify a failure reason into its failure category
        (temporary_failure, customer_action_required, checkout_abandonment,
        permanent_failure) without running the full workflow.
        """
        return classify_failure_reason(failure_reason)

    @mcp.tool()
    def estimate_recovery_probability(
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
        Run the ML model to estimate recovery probability for a payment.
        Returns the probability score and whether it clears the 0.55 policy threshold.
        """
        return predict_recovery_chance(
            amount=amount,
            payment_method=payment_method,
            failure_reason=failure_reason,
            attempt_count=attempt_count,
            customer_success_rate=customer_success_rate,
            previous_retry_success_rate=previous_retry_success_rate,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
        )

    return mcp


# ---------------------------------------------------------------------------
# Standalone entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    mcp_app = create_mcp_app()
    if mcp_app is None:
        raise SystemExit("MCP SDK not installed. Run: pip install 'mcp[cli]'")

    uvicorn.run(mcp_app, host="0.0.0.0", port=8001)
