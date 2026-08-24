import pandas as pd

from app.agents.diagnosis_agent import diagnose_payment
from app.agents.policy_guardian import evaluate_policy
from app.agents.recovery_planner import plan_recovery_action
from app.intelligence.classification.rules import classify_failure
from app.intelligence.features.feature_builder import build_features
from app.intelligence.models.predict import (
    load_model,
    predict_recovery_probability,
)
from app.workflows.state import RecoveryState


def classify_node(state: RecoveryState) -> dict:
    """
    Classify the payment failure using the existing deterministic rules.
    """

    failure_category = classify_failure(
        state["payment"].failure_reason
    )

    return {
        "classification": failure_category.value,
        "failure_category": failure_category,
    }


def predict_node(state: RecoveryState) -> dict:
    """
    Build ML features and predict recovery probability.
    """

    payment_record = state["payment"].model_dump()

    single_record_df = pd.DataFrame(
        [payment_record]
    )

    features, _ = build_features(
        single_record_df
    )

    model = load_model()

    recovery_probability = (
        predict_recovery_probability(
            model=model,
            features=features,
        )
    )

    return {
        "recovery_probability": recovery_probability,
    }


def diagnosis_node(state: RecoveryState) -> dict:
    """
    Produce a structured diagnosis using existing Day 4 logic.
    """

    diagnosis = diagnose_payment(
        payment=state["payment"],
        failure_category=state["failure_category"],
        recovery_probability=state[
            "recovery_probability"
        ],
    )

    return {
        "diagnosis": diagnosis,
    }


def planning_node(state: RecoveryState) -> dict:
    """
    Produce exactly one bounded recovery plan.
    """

    recovery_plan = plan_recovery_action(
        payment=state["payment"],
        failure_category=state["failure_category"],
        recovery_probability=state[
            "recovery_probability"
        ],
        diagnosis=state["diagnosis"],
    )

    return {
        "recovery_plan": recovery_plan,
        "expected_recovery_value": (
            recovery_plan.expected_recovery_value
        ),
        "priority_score": (
            recovery_plan.priority_score
        ),
    }


def policy_node(state: RecoveryState) -> dict:
    """
    Apply deterministic policy controls to the recovery plan.
    """

    policy_decision = evaluate_policy(
        payment=state["payment"],
        failure_category=state["failure_category"],
        recovery_probability=state[
            "recovery_probability"
        ],
        recovery_plan=state["recovery_plan"],
    )

    return {
        "policy_decision": policy_decision,
        "policy_approved": policy_decision.approved,
    }