from datetime import datetime, timezone
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.domain.enums.audit_stage import AuditStage
from app.domain.models.audit import AuditEvent
from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)
from app.tools.registry import ToolRegistry
from app.workflows.nodes import (
    classify_node,
    diagnosis_node,
    planning_node,
    policy_node,
    predict_node,
)
from app.workflows.router import route_after_policy
from app.workflows.state import RecoveryState
from app.workflows.verification import verify_node


def create_execution_audit_event(
    state: RecoveryState,
    action: str,
    result: str,
    decision: str,
    reason_codes: list[str] | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    """
    Create an audit event for a recovery action execution attempt.
    """

    return AuditEvent(
        audit_id=str(uuid4()),
        run_id=state.get(
            "run_id",
            f"execution_{state['payment'].payment_id}",
        ),
        payment_id=state["payment"].payment_id,
        timestamp=datetime.now(timezone.utc),
        stage=AuditStage.EXECUTION,
        input_summary=(
            f"Execution attempted for recovery action: {action}"
        ),
        decision=decision,
        reason_codes=reason_codes or [],
        actor="execute_node",
        result=result,
        metadata=metadata or {},
    )


def execute_node(
    state: RecoveryState,
) -> dict:
    """
    Execute an already policy-approved recovery action.

    This node is reached only through policy-controlled routing.
    """

    recovery_plan = state["recovery_plan"]
    action = recovery_plan.action

    execution_request = ExecutionRequest(
        run_id=state.get(
            "run_id",
            f"execution_{state['payment'].payment_id}",
        ),
        payment_id=state["payment"].payment_id,
        action=action,
        action_parameters=recovery_plan.action_parameters,
    )

    registry = ToolRegistry()

    tool = registry.get_tool(
        action,
    )

    if tool is None:
        result = ExecutionResult(
            success=False,
            action=action,
            message=(
                "No execution tool is registered for this "
                "recovery action."
            ),
            error_code="TOOL_NOT_REGISTERED",
        )

        audit_event = create_execution_audit_event(
            state=state,
            action=action.value,
            result="failed",
            decision="tool_not_registered",
            reason_codes=["TOOL_NOT_REGISTERED"],
            metadata={
                "error_code": result.error_code,
            },
        )

        return {
            "execution_result": result,
            "workflow_status": "EXECUTION_FAILED",
            "errors": [
                f"No tool registered for action: {action.value}",
            ],
            "audit_trail": [audit_event],
        }

    try:
        result = tool.execute(
            execution_request,
        )

    except Exception as exc:
        result = ExecutionResult(
            success=False,
            action=action,
            message="Tool execution failed.",
            error_code="TOOL_EXECUTION_ERROR",
        )

        audit_event = create_execution_audit_event(
            state=state,
            action=action.value,
            result="failed",
            decision="tool_execution_exception",
            reason_codes=["TOOL_EXECUTION_ERROR"],
            metadata={
                "error_code": result.error_code,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            },
        )

        return {
            "execution_result": result,
            "workflow_status": "EXECUTION_FAILED",
            "errors": [
                f"Tool execution error: {str(exc)}",
            ],
            "audit_trail": [audit_event],
        }

    if result.success:
        audit_event = create_execution_audit_event(
            state=state,
            action=action.value,
            result="success",
            decision="tool_execution_succeeded",
            metadata={
                "external_reference_id": (
                    result.external_reference_id
                ),
            },
        )

        return {
            "execution_result": result,
            "workflow_status": "EXECUTION_SUCCEEDED",
            "audit_trail": [audit_event],
        }

    audit_event = create_execution_audit_event(
        state=state,
        action=action.value,
        result="failed",
        decision="tool_execution_failed",
        reason_codes=[
            result.error_code
            if result.error_code is not None
            else "TOOL_EXECUTION_FAILED"
        ],
        metadata={
            "error_code": result.error_code,
            "message": result.message,
        },
    )

    return {
        "execution_result": result,
        "workflow_status": "EXECUTION_FAILED",
        "errors": [
            result.message,
        ],
        "audit_trail": [audit_event],
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

    workflow.add_node(
        "execute",
        execute_node,
    )

    workflow.add_node(
        "verify",
        verify_node,
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

    workflow.add_edge(
        "execute",
        "verify",
    )

    workflow.add_edge(
        "verify",
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