from langgraph.graph import END, START, StateGraph

from app.workflows.nodes import (
    classify_node,
    diagnosis_node,
    planning_node,
    policy_node,
    predict_node,
)
from app.workflows.router import route_after_policy
from app.workflows.state import RecoveryState


def execute_node(
    state: RecoveryState,
) -> dict:
    """
    Day 6 execution boundary placeholder.
    """

    return {
        "workflow_status": "EXECUTION_READY",
    }


def blocked_node(
    state: RecoveryState,
) -> dict:
    """
    Safe terminal path for policy-rejected actions.
    """

    return {
        "workflow_status": "POLICY_BLOCKED",
    }


def no_action_node(
    state: RecoveryState,
) -> dict:
    """
    Safe terminal path when no recovery action is required.
    """

    return {
        "workflow_status": "NO_ACTION_REQUIRED",
    }


def escalate_node(
    state: RecoveryState,
) -> dict:
    """
    Safe terminal path for merchant escalation.
    """

    return {
        "workflow_status": "MERCHANT_ESCALATION_REQUIRED",
    }

def build_recovery_graph():
    """
    Build the Recovery Brain LangGraph workflow.
    """

    workflow = StateGraph(RecoveryState)

    # Core workflow nodes
    workflow.add_node(
        "classify",
        classify_node,
    )

    workflow.add_node(
        "predict",
        predict_node,
    )

    workflow.add_node(
        "diagnose",
        diagnosis_node,
    )

    workflow.add_node(
        "plan",
        planning_node,
    )

    workflow.add_node(
        "policy",
        policy_node,
    )

    # Terminal path nodes
    workflow.add_node(
        "execute",
        execute_node,
    )

    workflow.add_node(
        "blocked",
        blocked_node,
    )

    workflow.add_node(
        "no_action",
        no_action_node,
    )

    workflow.add_node(
        "escalate",
        escalate_node,
    )

    # Main sequential flow
    workflow.add_edge(
        START,
        "classify",
    )

    workflow.add_edge(
        "classify",
        "predict",
    )

    workflow.add_edge(
        "predict",
        "diagnose",
    )

    workflow.add_edge(
        "diagnose",
        "plan",
    )

    workflow.add_edge(
        "plan",
        "policy",
    )

    # Policy-controlled routing
    workflow.add_conditional_edges(
        "policy",
        route_after_policy,
        {
            "execute": "execute",
            "blocked": "blocked",
            "no_action": "no_action",
            "escalate": "escalate",
        },
    )

    # All terminal paths end safely
    workflow.add_edge(
        "execute",
        END,
    )

    workflow.add_edge(
        "blocked",
        END,
    )

    workflow.add_edge(
        "no_action",
        END,
    )

    workflow.add_edge(
        "escalate",
        END,
    )

    return workflow.compile()