"""
Dashboard Service

Aggregates metrics, batch lists, and per-run drill-downs from the SQLite DB.
All serialisation bugs that caused approved/blocked counts to always be 0 and
field-name mismatches in batch listings are fixed here.
"""

from __future__ import annotations

import logging
from typing import Any

from app.api.schemas.dashboard import (
    BatchRecordSummary,
    DashboardMetricsResponse,
    PaymentDrillDownResponse,
)
from app.core.database import SessionLocal
from app.data.models import AuditRecord, RunRecord

logger = logging.getLogger(__name__)

# Workflow statuses that count as successfully recovered
RECOVERED_STATUSES = {"RECOVERY_VERIFIED", "EXECUTION_SUCCEEDED"}

# Workflow statuses that count as unresolved exceptions
EXCEPTION_STATUSES = {"ERROR", "FAILED", "EXECUTION_FAILED"}


def _safe_dict(obj: Any) -> dict:
    """Coerce a state-snapshot value into a plain dict."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return {}


class DashboardService:
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_metrics(self) -> DashboardMetricsResponse:
        with SessionLocal() as db:
            runs = db.query(RunRecord).all()
            total_processed = len(runs)

            revenue_at_risk = 0.0
            predicted_recoverable = 0.0
            actually_recovered = 0.0
            actions_approved = 0
            actions_blocked = 0
            unresolved_exceptions = 0

            for run in runs:
                state: dict = run.state_snapshot or {}

                # ── payment amount ────────────────────────────────────────
                payment = _safe_dict(state.get("payment", {}))
                amount = float(payment.get("amount", 0.0))
                revenue_at_risk += amount

                # ── predicted recoverable ─────────────────────────────────
                prob = float(state.get("recovery_probability") or 0.0)
                predicted_recoverable += amount * prob

                # ── actually recovered ────────────────────────────────────
                actually_recovered += float(run.recovered_amount or 0.0)

                # ── policy decision: use the 'approved' boolean key ───────
                # The snapshot stores PolicyDecision as {"approved": bool, ...}
                policy = _safe_dict(state.get("policy_decision", {}))
                approved: bool | None = policy.get("approved")
                if approved is True:
                    actions_approved += 1
                elif approved is False:
                    actions_blocked += 1

                # ── unresolved exceptions ─────────────────────────────────
                if (run.workflow_status or "").upper() in EXCEPTION_STATUSES:
                    unresolved_exceptions += 1

            recovery_rate = (
                (actually_recovered / revenue_at_risk * 100)
                if revenue_at_risk > 0
                else 0.0
            )

            return DashboardMetricsResponse(
                total_processed=total_processed,
                revenue_at_risk=round(revenue_at_risk, 2),
                predicted_recoverable=round(predicted_recoverable, 2),
                actually_recovered=round(actually_recovered, 2),
                recovery_rate=round(recovery_rate, 2),
                actions_approved=actions_approved,
                actions_blocked=actions_blocked,
                unresolved_exceptions=unresolved_exceptions,
            )

    def get_batches(self) -> list[BatchRecordSummary]:
        with SessionLocal() as db:
            runs = (
                db.query(RunRecord)
                .order_by(RunRecord.created_at.desc())
                .all()
            )
            batches: list[BatchRecordSummary] = []

            for run in runs:
                state: dict = run.state_snapshot or {}

                payment = _safe_dict(state.get("payment", {}))
                amount = float(payment.get("amount", 0.0))

                classification = state.get("classification") or "unknown"
                prob = float(state.get("recovery_probability") or 0.0)

                # ── recovery plan ─────────────────────────────────────────
                # Stored as {"action": "retry_now", ...}  (enum .value)
                plan = _safe_dict(state.get("recovery_plan", {}))
                recommended_action = plan.get("action") or "none"

                # ── policy decision ───────────────────────────────────────
                policy = _safe_dict(state.get("policy_decision", {}))
                approved = policy.get("approved")
                if approved is True:
                    policy_str = "APPROVED"
                elif approved is False:
                    policy_str = "BLOCKED"
                else:
                    policy_str = "PENDING"

                # ── execution result ──────────────────────────────────────
                exec_res = _safe_dict(state.get("execution_result", {}))
                if exec_res.get("success") is True:
                    exec_status = "SUCCESS"
                elif exec_res.get("success") is False:
                    exec_status = "FAILED"
                else:
                    exec_status = run.workflow_status or "PENDING"

                # ── verification result ───────────────────────────────────
                verif_res = _safe_dict(state.get("verification_result", {}))
                if verif_res.get("verified") is True:
                    verif_status = "VERIFIED"
                elif verif_res.get("verified") is False:
                    verif_status = "NOT_VERIFIED"
                else:
                    verif_status = "PENDING"

                batches.append(
                    BatchRecordSummary(
                        run_id=run.run_id,
                        payment_id=run.payment_id,
                        amount=amount,
                        failure_category=classification,
                        recovery_probability=round(prob, 4),
                        expected_recovery_value=round(amount * prob, 2),
                        recommended_action=recommended_action,
                        policy_decision=policy_str,
                        execution_status=exec_status,
                        verification_status=verif_status,
                        recovered_amount=float(run.recovered_amount or 0.0),
                        workflow_status=run.workflow_status or "PENDING",
                        timestamp=run.created_at,
                    )
                )

            return batches

    def get_payment_details(self, run_id: str) -> PaymentDrillDownResponse | None:
        with SessionLocal() as db:
            run = (
                db.query(RunRecord)
                .filter(RunRecord.run_id == run_id)
                .first()
            )
            if not run:
                return None

            audits = (
                db.query(AuditRecord)
                .filter(AuditRecord.run_id == run_id)
                .order_by(AuditRecord.timestamp)
                .all()
            )

            audit_list = [
                {
                    "audit_id": a.audit_id,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                    "stage": a.stage,
                    "actor": a.actor,
                    "decision": a.decision,
                    "reason_codes": a.reason_codes or [],
                    "result": a.result,
                    "input_summary": a.input_summary,
                    "metadata": a.metadata_json or {},
                }
                for a in audits
            ]

            state: dict = run.state_snapshot or {}
            payment_info = _safe_dict(state.get("payment", {}))
            diagnosis = _safe_dict(state.get("diagnosis", {}))
            recovery_plan = _safe_dict(state.get("recovery_plan", {}))
            policy_guardian = _safe_dict(state.get("policy_decision", {}))
            execution = _safe_dict(state.get("execution_result", {}))

            return PaymentDrillDownResponse(
                payment_info=payment_info,
                intelligence={
                    "classification": state.get("classification"),
                    "recovery_probability": state.get("recovery_probability"),
                    "expected_recovery_value": state.get("expected_recovery_value"),
                    "priority_score": state.get("priority_score"),
                },
                diagnosis=diagnosis,
                recovery_plan=recovery_plan,
                policy_guardian=policy_guardian,
                execution=execution,
                audit_trail=audit_list,
                workflow_status=run.workflow_status or "UNKNOWN",
            )
