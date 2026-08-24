from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import (
    ExecutionResult,
    RecoveryPlan,
)
from app.workflows.graph import execute_node


def make_state() -> dict:
    return {
        "payment": PaymentRiskRecord(
            payment_id="pay_failure_001",
            customer_id="cust_failure_001",
            merchant_id="merchant_001",
            amount=5000.0,
            currency="INR",
            payment_method="upi",
            status="failed",
            failure_reason="bank_timeout",
            attempt_count=1,
            event_timestamp="2026-08-25T12:00:00",
            customer_success_rate=0.90,
            previous_retry_success_rate=0.80,
            contact_count=0,
            actual_recovery_outcome=0,
        ),
        "recovery_plan": RecoveryPlan(
            action=RecoveryAction.RETRY_NOW,
            expected_recovery_value=4000.0,
            priority_score=0.8,
        ),
    }


def test_execute_node_handles_tool_returning_failure(
    monkeypatch,
) -> None:
    class FailingTool:
        def execute(self, state):
            return ExecutionResult(
                success=False,
                action=RecoveryAction.RETRY_NOW,
                message="Mock external payment retry failed.",
                error_code="MOCK_EXTERNAL_FAILURE",
            )

    class FailingRegistry:
        def get_tool(self, action):
            return FailingTool()

    monkeypatch.setattr(
        "app.tools.service.ToolRegistry",
        FailingRegistry,
    )

    result = execute_node(
        make_state(),
    )

    assert result["workflow_status"] == "EXECUTION_FAILED"

    assert result["execution_result"].success is False

    assert (
        result["execution_result"].error_code
        == "MOCK_EXTERNAL_FAILURE"
    )

    assert result["errors"] == [
        "Mock external payment retry failed.",
    ]