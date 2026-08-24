from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import RecoveryPlan
from app.workflows.factory import create_recovery_state
from app.workflows.graph import execute_node
from app.workflows.verification import verify_node


def make_state() -> dict:
    payment = PaymentRiskRecord(
        payment_id="pay_lifecycle_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        amount=5000.0,
        currency="INR",
        payment_method="upi",
        status="failed",
        failure_reason="bank_timeout",
        attempt_count=1,
        event_timestamp="2026-08-25T10:30:00",
        customer_success_rate=0.90,
        previous_retry_success_rate=0.80,
        contact_count=0,
        actual_recovery_outcome=1,
    )

    state = create_recovery_state(
        run_id="run_lifecycle_001",
        payment=payment,
    )

    state["recovery_plan"] = RecoveryPlan(
        action=RecoveryAction.RETRY_NOW,
        expected_recovery_value=4000.0,
        priority_score=0.8,
    )

    return state


def test_successful_execution_and_verification_lifecycle() -> None:
    state = make_state()

    execution_update = execute_node(state)

    assert (
        execution_update["workflow_status"]
        == "EXECUTION_SUCCEEDED"
    )

    assert execution_update["execution_result"].success is True

    assert len(execution_update["audit_trail"]) == 1

    state.update(execution_update)

    verification_update = verify_node(state)

    assert (
        verification_update["workflow_status"]
        == "RECOVERY_VERIFIED"
    )

    assert (
        verification_update["verification_result"].verified
        is True
    )

    assert (
        verification_update["recovered_amount"]
        == 4000.0
    )


def test_failed_execution_cannot_be_verified() -> None:
    state = make_state()

    state["recovery_plan"] = RecoveryPlan(
        action=RecoveryAction.DO_NOTHING,
        expected_recovery_value=0.0,
        priority_score=0.0,
    )

    execution_update = execute_node(state)

    assert (
        execution_update["workflow_status"]
        == "EXECUTION_FAILED"
    )

    assert execution_update["execution_result"].success is False

    state.update(execution_update)

    verification_update = verify_node(state)

    assert (
        verification_update["workflow_status"]
        == "RECOVERY_NOT_VERIFIED"
    )

    assert (
        verification_update["verification_result"].verified
        is False
    )

    assert (
        verification_update["recovered_amount"]
        == 0.0
    )