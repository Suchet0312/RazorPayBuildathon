"""
Recovery Routes

Endpoints:
  POST /recovery/analyze          – single payment (async background)
  POST /recovery/analyze/sync     – single payment (synchronous, for testing/MCP)
  POST /recovery/batch            – batch of up to 100 payments
  GET  /recovery/status/{run_id}  – poll async run status
  POST /recovery/promise-to-pay   – record a promise-to-pay commitment
  POST /recovery/hinglish         – send a Hinglish voice/SMS recovery nudge
  POST /recovery/simulate-failure – run a real failure scenario through the full workflow
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.schemas.requests import (
    BatchAnalyzeRequest,
    HinglishRecoveryRequest,
    PromiseToPayRequest,
    RecoveryAnalyzeRequest,
)
from app.api.schemas.responses import (
    BatchAnalyzeResponse,
    HinglishRecoveryResponse,
    PromiseToPayResponse,
    RecoveryAnalyzeResponse,
    RecoveryStatusResponse,
)
from app.services.hinglish_service import HinglishService
from app.services.promise_to_pay_service import PromiseToPayService
from app.services.recovery_service import RecoveryService

router = APIRouter(prefix="/recovery", tags=["recovery"])
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dependency factories
# ---------------------------------------------------------------------------

def get_recovery_service() -> RecoveryService:
    return RecoveryService()


def get_ptp_service() -> PromiseToPayService:
    return PromiseToPayService()


def get_hinglish_service() -> HinglishService:
    return HinglishService()


# ---------------------------------------------------------------------------
# Single-payment async (fire-and-forget)
# ---------------------------------------------------------------------------

@router.post("/analyze", response_model=RecoveryAnalyzeResponse)
async def analyze_payment(
    request: RecoveryAnalyzeRequest,
    background_tasks: BackgroundTasks,
    service: RecoveryService = Depends(get_recovery_service),
) -> RecoveryAnalyzeResponse:
    """
    Start the recovery workflow asynchronously.

    Returns immediately with a run_id. Poll GET /recovery/status/{run_id}
    for the final result.
    """
    try:
        run_id = service.analyze_payment_async(request)
        background_tasks.add_task(
            service.execute_workflow_in_background, request, run_id
        )
        return RecoveryAnalyzeResponse(
            run_id=run_id,
            workflow_status="PENDING",
            message="Workflow execution started in background.",
        )
    except Exception as exc:
        logger.error("Unexpected error in /analyze: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------------------------------------------------------------
# Single-payment synchronous (useful for testing + MCP)
# ---------------------------------------------------------------------------

@router.post("/analyze/sync", response_model=RecoveryAnalyzeResponse)
async def analyze_payment_sync(
    request: RecoveryAnalyzeRequest,
    service: RecoveryService = Depends(get_recovery_service),
) -> RecoveryAnalyzeResponse:
    """
    Run the full recovery workflow synchronously and return the complete result.
    Slower than /analyze but the response contains the full decision breakdown.
    """
    try:
        return service.analyze_payment(request)
    except Exception as exc:
        logger.error("Unexpected error in /analyze/sync: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

@router.post("/batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(
    request: BatchAnalyzeRequest,
    service: RecoveryService = Depends(get_recovery_service),
) -> BatchAnalyzeResponse:
    """
    Run the recovery workflow across a batch of payments (max 100).

    Returns aggregate metrics (revenue at risk, predicted recoverable,
    actually recovered) alongside per-payment results and audit trails.
    This is the 'Show measured money recovered across a batch' capability
    from the spec.
    """
    try:
        return service.analyze_batch(request.payments, stop_on_error=request.stop_on_error)
    except Exception as exc:
        logger.error("Unexpected error in /batch: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------------------------------------------------------------
# Status polling
# ---------------------------------------------------------------------------

@router.get("/status/{run_id}", response_model=RecoveryStatusResponse)
async def get_recovery_status(
    run_id: str,
    service: RecoveryService = Depends(get_recovery_service),
) -> RecoveryStatusResponse:
    status = service.get_status(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Run not found")
    return RecoveryStatusResponse(**status)


# ---------------------------------------------------------------------------
# Promise-to-Pay tracker
# ---------------------------------------------------------------------------

@router.post("/promise-to-pay", response_model=PromiseToPayResponse)
async def record_promise_to_pay(
    request: PromiseToPayRequest,
    service: PromiseToPayService = Depends(get_ptp_service),
) -> PromiseToPayResponse:
    """
    Record a customer's payment commitment and schedule follow-up nudges.

    This implements the 'Promise-to-pay tracker' feature from the spec:
    captures the commitment window, schedules two follow-ups, and returns
    a reference ID for downstream tracking.
    """
    try:
        return service.record_commitment(request)
    except Exception as exc:
        logger.error("Error in /promise-to-pay: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------------------------------------------------------------
# Hinglish voice/SMS recovery
# ---------------------------------------------------------------------------

@router.post("/hinglish", response_model=HinglishRecoveryResponse)
async def hinglish_recovery(
    request: HinglishRecoveryRequest,
    service: HinglishService = Depends(get_hinglish_service),
) -> HinglishRecoveryResponse:
    """
    Dispatch a Hinglish (Hindi + English) recovery nudge via SMS, voice, or
    WhatsApp — implementing the 'Hinglish voice recovery' feature from the spec.
    """
    try:
        return service.dispatch(request)
    except Exception as exc:
        logger.error("Error in /hinglish: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------------------------------------------------------------
# Simulate failure (real workflow with a failure scenario)
# ---------------------------------------------------------------------------

SIMULATE_FAILURE_PAYMENT = RecoveryAnalyzeRequest(
    payment_id="sim_fail_001",
    customer_id="cust_demo",
    merchant_id="merch_demo",
    amount=4999.0,
    currency="INR",
    payment_method="upi",
    status="failed",
    failure_reason="bank_timeout",  # guaranteed TEMPORARY_FAILURE path
    attempt_count=0,
    event_timestamp=datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc),
    customer_success_rate=0.72,
    previous_retry_success_rate=0.68,
    contact_count=0,
)


@router.post("/simulate-failure")
async def simulate_failure(
    service: RecoveryService = Depends(get_recovery_service),
) -> dict:
    """
    Run a real recovery workflow with a pre-configured 'bank_timeout' scenario.

    Unlike the old mocked response this actually invokes the LangGraph pipeline,
    producing a genuine classification → prediction → diagnosis → plan → policy
    → execution → verification result with a full audit trail.
    """
    try:
        result = service.analyze_payment(SIMULATE_FAILURE_PAYMENT)
        plan = result.recovery_plan
        policy = result.policy_decision
        exec_res = result.execution_result

        return {
            "status": result.workflow_status,
            "run_id": result.run_id,
            "scenario": "bank_timeout – TEMPORARY_FAILURE",
            "classification": result.classification,
            "recovery_probability": result.recovery_probability,
            "recommended_action": (
                plan.action.value
                if hasattr(plan, "action")
                else (plan.get("action") if isinstance(plan, dict) else None)
            ),
            "policy_approved": (
                policy.approved
                if hasattr(policy, "approved")
                else (policy.get("approved") if isinstance(policy, dict) else None)
            ),
            "execution_success": (
                exec_res.success
                if exec_res and hasattr(exec_res, "success")
                else (exec_res.get("success") if isinstance(exec_res, dict) else None)
            ),
            "recovered_amount": result.recovered_amount,
            "errors": result.errors or [],
            "message": (
                "Full workflow executed successfully. Check run_id for audit trail."
            ),
        }
    except Exception as exc:
        logger.error("Error in /simulate-failure: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
