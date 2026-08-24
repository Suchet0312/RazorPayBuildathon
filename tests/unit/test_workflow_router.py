from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import RecoveryPlan
from app.workflows.router import route_after_policy


def build_state(
    *,
    policy_approved: bool,
    action: RecoveryAction,
) -> dict:
    recovery_plan = RecoveryPlan(
        action=action,
        action_parameters={},
        reason_codes=[],
        expected_recovery_value=0.0,
        priority_score=0.0,
    )

    return {
        "policy_approved": policy_approved,
        "recovery_plan": recovery_plan,
    }


def test_rejected_policy_routes_to_blocked() -> None:
    state = build_state(
        policy_approved=False,
        action=RecoveryAction.RETRY_NOW,
    )

    assert route_after_policy(state) == "blocked"


def test_do_nothing_routes_to_no_action() -> None:
    state = build_state(
        policy_approved=True,
        action=RecoveryAction.DO_NOTHING,
    )

    assert route_after_policy(state) == "no_action"


def test_merchant_escalation_routes_to_escalate() -> None:
    state = build_state(
        policy_approved=True,
        action=RecoveryAction.ESCALATE_TO_MERCHANT,
    )

    assert route_after_policy(state) == "escalate"


def test_approved_automated_action_routes_to_execute() -> None:
    state = build_state(
        policy_approved=True,
        action=RecoveryAction.RETRY_NOW,
    )

    assert route_after_policy(state) == "execute"