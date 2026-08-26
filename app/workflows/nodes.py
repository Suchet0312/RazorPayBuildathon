from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd

from app.agents.diagnosis_agent import diagnose_payment
from app.agents.policy_guardian import evaluate_policy
from app.agents.recovery_planner import plan_recovery_action
from app.domain.enums.audit_stage import AuditStage
from app.domain.models.audit import AuditEvent
from app.intelligence.classification.rules import classify_failure
from app.intelligence.features.feature_builder import build_features
from app.intelligence.models.predict import (
    load_model,
    predict_recovery_probability,
)
from app.workflows.state import RecoveryState


# ---------------------------------------------------------------------------
# Audit helper
# ---------------------------------------------------------------------------

def _make_audit(
    state: RecoveryState,
    stage: AuditStage,
    actor: str,
    decision: str,
    result: str,
    input_summary: str,
    reason_codes: list[str] | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    return AuditEvent(
        audit_id=str(uuid4()),
        run_id=state.get("run_id", "unknown"),
        payment_id=state["payment"].payment_id,
        timestamp=datetime.now(timezone.utc),
        stage=stage,
        input_summary=input_summary,
        decision=decision,
        reason_codes=reason_codes or [],
        actor=actor,
        result=result,
        metadata=metadata or {},
    )


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def classify_node(state: RecoveryState) -> dict:
    """Classify the payment failure using deterministic rules."""

    failure_reason = state["payment"].failure_reason or "unknown"
    failure_category = classify_failure(failure_reason)

    audit = _make_audit(
        state=state,
        stage=AuditStage.CLASSIFICATION,
        actor="classify_node",
        decision=failure_category.value,
        result="classified",
        input_summary=f"Failure reason: '{failure_reason}'",
        reason_codes=[failure_category.value.upper()],
        metadata={"failure_reason": failure_reason},
    )

    return {
        "classification": failure_category.value,
        "failure_category": failure_category,
        "audit_trail": [audit],
    }


def predict_node(state: RecoveryState) -> dict:
    """Build ML features and predict recovery probability."""

    payment_record = state["payment"].model_dump()
    single_record_df = pd.DataFrame([payment_record])

    features, _ = build_features(single_record_df)
    model = load_model()
    recovery_probability = predict_recovery_probability(
        model=model,
        features=features,
    )

    audit = _make_audit(
        state=state,
        stage=AuditStage.PREDICTION,
        actor="predict_node",
        decision="probability_computed",
        result=f"{recovery_probability:.4f}",
        input_summary=(
            f"ML prediction for payment "
            f"{state['payment'].payment_id} "
            f"(method={state['payment'].payment_method}, "
            f"amount={state['payment'].amount})"
        ),
        metadata={"recovery_probability": recovery_probability},
    )

    return {
        "recovery_probability": recovery_probability,
        "audit_trail": [audit],
    }


def diagnosis_node(state: RecoveryState) -> dict:
    """Produce a structured diagnosis."""

    diagnosis = diagnose_payment(
        payment=state["payment"],
        failure_category=state["failure_category"],
        recovery_probability=state["recovery_probability"],
    )

    audit = _make_audit(
        state=state,
        stage=AuditStage.DIAGNOSIS,
        actor="diagnosis_node",
        decision="diagnosis_complete",
        result="success",
        input_summary=(
            f"Diagnosis for {state['payment'].payment_id}: "
            f"category={state['failure_category'].value}, "
            f"prob={state['recovery_probability']:.3f}"
        ),
        reason_codes=diagnosis.reason_codes,
        metadata={
            "confidence": diagnosis.confidence,
            "summary": diagnosis.summary,
        },
    )

    return {
        "diagnosis": diagnosis,
        "audit_trail": [audit],
    }


def planning_node(state: RecoveryState) -> dict:
    """Produce exactly one bounded recovery plan."""

    recovery_plan = plan_recovery_action(
        payment=state["payment"],
        failure_category=state["failure_category"],
        recovery_probability=state["recovery_probability"],
        diagnosis=state["diagnosis"],
    )

    audit = _make_audit(
        state=state,
        stage=AuditStage.PLANNING,
        actor="planning_node",
        decision=recovery_plan.action.value,
        result="plan_selected",
        input_summary=(
            f"Planning for {state['payment'].payment_id}: "
            f"prob={state['recovery_probability']:.3f}, "
            f"amount={state['payment'].amount}"
        ),
        reason_codes=recovery_plan.reason_codes,
        metadata={
            "action": recovery_plan.action.value,
            "expected_recovery_value": recovery_plan.expected_recovery_value,
            "priority_score": recovery_plan.priority_score,
            "action_parameters": recovery_plan.action_parameters,
        },
    )

    return {
        "recovery_plan": recovery_plan,
        "expected_recovery_value": recovery_plan.expected_recovery_value,
        "priority_score": recovery_plan.priority_score,
        "audit_trail": [audit],
    }


def policy_node(state: RecoveryState) -> dict:
    """Apply deterministic policy controls to the recovery plan."""

    policy_decision = evaluate_policy(
        payment=state["payment"],
        failure_category=state["failure_category"],
        recovery_probability=state["recovery_probability"],
        recovery_plan=state["recovery_plan"],
    )

    audit = _make_audit(
        state=state,
        stage=AuditStage.POLICY_GATE,
        actor="policy_node",
        decision="approved" if policy_decision.approved else "blocked",
        result="approved" if policy_decision.approved else "blocked",
        input_summary=(
            f"Policy check for action "
            f"'{state['recovery_plan'].action.value}' "
            f"on payment {state['payment'].payment_id}"
        ),
        reason_codes=policy_decision.reason_codes,
        metadata={
            "approved": policy_decision.approved,
            "reason": policy_decision.reason,
            "action": state["recovery_plan"].action.value,
        },
    )

    return {
        "policy_decision": policy_decision,
        "policy_approved": policy_decision.approved,
        "audit_trail": [audit],
    }
