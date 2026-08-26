"""
Recovery Service

Bridges the FastAPI routes to the LangGraph recovery workflow.
Supports both synchronous (batch / MCP) and async background execution.
"""

from __future__ import annotations

import logging
from uuid import uuid4

from app.api.schemas.requests import RecoveryAnalyzeRequest
from app.api.schemas.responses import (
    BatchAnalyzeResponse,
    BatchPaymentResult,
    RecoveryAnalyzeResponse,
)
from app.core.database import SessionLocal
from app.core.logging import RecoveryLogger
from app.domain.models.payment import PaymentRiskRecord
from app.repositories.recovery_repository import RecoveryRepository
from app.workflows.factory import create_recovery_state
from app.workflows.graph import build_recovery_graph

logger = logging.getLogger(__name__)


class RecoveryService:
    def __init__(self) -> None:
        self.graph = build_recovery_graph()

    # ------------------------------------------------------------------
    # Synchronous single-payment analysis (used by batch + MCP)
    # ------------------------------------------------------------------

    def analyze_payment(self, request: RecoveryAnalyzeRequest) -> RecoveryAnalyzeResponse:
        run_id = str(uuid4())
        payment_record = _to_domain(request)
        initial_state = create_recovery_state(run_id=run_id, payment=payment_record)

        wf_logger = RecoveryLogger(run_id=run_id, payment_id=request.payment_id)
        try:
            wf_logger.info("Invoking recovery graph (sync)")
            final_state = self.graph.invoke(initial_state)

            with SessionLocal() as db:
                RecoveryRepository(db).save_run(final_state)

            return _state_to_response(final_state)

        except Exception as exc:
            wf_logger.error("Error during graph invocation", exc_info=True)
            return RecoveryAnalyzeResponse(
                run_id=run_id,
                workflow_status="ERROR",
                errors=[str(exc)],
            )

    # ------------------------------------------------------------------
    # Async background (used by the /analyze endpoint)
    # ------------------------------------------------------------------

    def analyze_payment_async(self, request: RecoveryAnalyzeRequest) -> str:
        """Save a PENDING record and return a run_id immediately."""
        run_id = str(uuid4())
        payment_record = _to_domain(request)
        with SessionLocal() as db:
            RecoveryRepository(db).save_run({
                "run_id": run_id,
                "payment": payment_record,
                "workflow_status": "PENDING",
                "recovered_amount": 0.0,
                "audit_trail": [],
                "errors": [],
                "policy_approved": False,
            })
        return run_id

    def execute_workflow_in_background(
        self, request: RecoveryAnalyzeRequest, run_id: str
    ) -> None:
        payment_record = _to_domain(request)
        initial_state = create_recovery_state(run_id=run_id, payment=payment_record)
        wf_logger = RecoveryLogger(run_id=run_id, payment_id=request.payment_id)
        try:
            wf_logger.info("Background graph execution")
            final_state = self.graph.invoke(initial_state)
            with SessionLocal() as db:
                RecoveryRepository(db).save_run(final_state)
        except Exception as exc:
            wf_logger.error(f"Error in background execution: {exc}", exc_info=True)
            with SessionLocal() as db:
                RecoveryRepository(db).save_run({
                    "run_id": run_id,
                    "payment": payment_record,
                    "workflow_status": "ERROR",
                    "recovered_amount": 0.0,
                    "audit_trail": [],
                    "errors": [str(exc)],
                    "policy_approved": False,
                })

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def analyze_batch(
        self,
        requests: list[RecoveryAnalyzeRequest],
        stop_on_error: bool = False,
    ) -> BatchAnalyzeResponse:
        results: list[BatchPaymentResult] = []
        succeeded = 0
        failed = 0
        total_risk = 0.0
        total_predicted = 0.0
        total_recovered = 0.0

        for req in requests:
            total_risk += req.amount
            try:
                resp = self.analyze_payment(req)

                prob = resp.recovery_probability or 0.0
                total_predicted += req.amount * prob
                recovered = resp.recovered_amount or 0.0
                total_recovered += recovered

                plan = resp.recovery_plan
                action = None
                if isinstance(plan, dict):
                    action = plan.get("action")
                elif hasattr(plan, "action"):
                    action = plan.action.value if hasattr(plan.action, "value") else str(plan.action)

                policy = resp.policy_decision
                approved = None
                if isinstance(policy, dict):
                    approved = policy.get("approved")
                elif hasattr(policy, "approved"):
                    approved = policy.approved

                errors = resp.errors or []
                results.append(BatchPaymentResult(
                    payment_id=req.payment_id,
                    run_id=resp.run_id,
                    workflow_status=resp.workflow_status,
                    recovery_probability=prob,
                    recommended_action=action,
                    policy_approved=approved,
                    recovered_amount=recovered,
                    error=errors[0] if errors else None,
                ))

                if resp.workflow_status in {"ERROR"} and stop_on_error:
                    failed += 1
                    break
                else:
                    succeeded += 1

            except Exception as exc:
                logger.error("Batch item failed for %s: %s", req.payment_id, exc)
                results.append(BatchPaymentResult(
                    payment_id=req.payment_id,
                    workflow_status="ERROR",
                    error=str(exc),
                ))
                failed += 1
                if stop_on_error:
                    break

        return BatchAnalyzeResponse(
            total=len(requests),
            succeeded=succeeded,
            failed=failed,
            total_revenue_at_risk=round(total_risk, 2),
            total_predicted_recoverable=round(total_predicted, 2),
            total_actually_recovered=round(total_recovered, 2),
            results=results,
        )

    # ------------------------------------------------------------------
    # Status lookup
    # ------------------------------------------------------------------

    def get_status(self, run_id: str) -> dict | None:
        with SessionLocal() as db:
            return RecoveryRepository(db).get_run_status(run_id)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_domain(request: RecoveryAnalyzeRequest) -> PaymentRiskRecord:
    return PaymentRiskRecord(
        payment_id=request.payment_id,
        customer_id=request.customer_id,
        merchant_id=request.merchant_id,
        amount=request.amount,
        currency=request.currency,
        payment_method=request.payment_method,
        status=request.status,
        failure_reason=request.failure_reason,
        attempt_count=request.attempt_count,
        event_timestamp=request.event_timestamp,
        customer_success_rate=request.customer_success_rate,
        previous_retry_success_rate=request.previous_retry_success_rate,
        contact_count=request.contact_count,
    )


def _state_to_response(state: dict) -> RecoveryAnalyzeResponse:
    return RecoveryAnalyzeResponse(
        run_id=state.get("run_id"),
        classification=state.get("classification"),
        recovery_probability=state.get("recovery_probability"),
        recovery_plan=state.get("recovery_plan"),
        policy_decision=state.get("policy_decision"),
        execution_result=state.get("execution_result"),
        verification_result=state.get("verification_result"),
        workflow_status=state.get("workflow_status"),
        recovered_amount=state.get("recovered_amount"),
        errors=state.get("errors", []),
    )
