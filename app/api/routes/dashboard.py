"""
Dashboard Routes

GET /api/v1/dashboard/metrics                      – aggregated metrics
GET /api/v1/dashboard/recovery-batches             – all runs (summary list)
GET /api/v1/dashboard/recovery-batches/{run_id}    – per-run drill-down
POST /api/v1/dashboard/demo/simulate-failure       – delegates to /recovery/simulate-failure
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.dashboard import (
    BatchRecordSummary,
    DashboardMetricsResponse,
    FailureDemoResponse,
    PaymentDrillDownResponse,
)
from app.services.dashboard_service import DashboardService
from app.services.recovery_service import RecoveryService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)


def get_dashboard_service() -> DashboardService:
    return DashboardService()


def get_recovery_service() -> RecoveryService:
    return RecoveryService()


@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_metrics(
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardMetricsResponse:
    try:
        return service.get_metrics()
    except Exception as exc:
        logger.error("Error fetching metrics: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/recovery-batches", response_model=List[BatchRecordSummary])
async def get_recovery_batches(
    service: DashboardService = Depends(get_dashboard_service),
) -> List[BatchRecordSummary]:
    try:
        return service.get_batches()
    except Exception as exc:
        logger.error("Error fetching batches: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/recovery-batches/{run_id}", response_model=PaymentDrillDownResponse)
async def get_payment_drill_down(
    run_id: str,
    service: DashboardService = Depends(get_dashboard_service),
) -> PaymentDrillDownResponse:
    try:
        result = service.get_payment_details(run_id)
        if not result:
            raise HTTPException(status_code=404, detail="Run not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error fetching payment details for run %s: %s", run_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/demo/simulate-failure", response_model=FailureDemoResponse)
async def simulate_failure_demo(
    recovery_service: RecoveryService = Depends(get_recovery_service),
) -> FailureDemoResponse:
    """
    Runs a real failure scenario through the full workflow and returns a
    FailureDemoResponse shaped for the demo UI.
    """
    from datetime import datetime, timezone
    from app.api.schemas.requests import RecoveryAnalyzeRequest

    demo_request = RecoveryAnalyzeRequest(
        payment_id="demo_fail_ui",
        customer_id="cust_demo_ui",
        merchant_id="merch_demo_ui",
        amount=2500.0,
        currency="INR",
        payment_method="netbanking",
        status="failed",
        failure_reason="bank_timeout",
        attempt_count=0,
        event_timestamp=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
        customer_success_rate=0.70,
        previous_retry_success_rate=0.65,
        contact_count=0,
    )

    try:
        result = recovery_service.analyze_payment(demo_request)

        # Build a friendly audit trail from the structured result
        audit_items = []
        if result.classification:
            audit_items.append({
                "stage": "CLASSIFICATION",
                "actor": "classify_node",
                "decision": "PROCEED",
                "result": result.classification,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        if result.recovery_probability is not None:
            audit_items.append({
                "stage": "ML_PREDICTION",
                "actor": "predict_node",
                "decision": "PROCEED",
                "result": f"Probability {result.recovery_probability:.0%}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        if result.recovery_plan:
            plan = result.recovery_plan
            action = plan.action.value if hasattr(plan, "action") else plan.get("action", "unknown")
            audit_items.append({
                "stage": "RECOVERY_PLAN",
                "actor": "planning_node",
                "decision": "PROCEED",
                "result": action.upper(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        if result.policy_decision:
            policy = result.policy_decision
            approved = policy.approved if hasattr(policy, "approved") else policy.get("approved")
            audit_items.append({
                "stage": "POLICY_GUARDIAN",
                "actor": "policy_node",
                "decision": "APPROVED" if approved else "BLOCKED",
                "result": "Approved" if approved else "Blocked",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        if result.execution_result:
            exec_r = result.execution_result
            success = exec_r.success if hasattr(exec_r, "success") else exec_r.get("success")
            audit_items.append({
                "stage": "EXECUTION",
                "actor": "execute_node",
                "decision": "SUCCESS" if success else "FAILED",
                "result": exec_r.message if hasattr(exec_r, "message") else exec_r.get("message", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        return FailureDemoResponse(
            status=result.workflow_status or "UNKNOWN",
            message=f"Demo workflow complete. Status: {result.workflow_status}",
            run_id=result.run_id or "unknown",
            audit_trail=audit_items,
        )

    except Exception as exc:
        logger.error("simulate_failure_demo error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
