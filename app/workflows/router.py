from app.domain.enums.recovery_action import RecoveryAction
from app.workflows.state import RecoveryState


def route_after_policy(
    state: RecoveryState,
) -> str:
    """
    Decide the terminal workflow path after policy evaluation.

    No executable action may proceed unless policy approval exists.
    """

    if not state["policy_approved"]:
        return "blocked"

    action = state["recovery_plan"].action

    if action == RecoveryAction.DO_NOTHING:
        return "no_action"

    if action == RecoveryAction.ESCALATE_TO_MERCHANT:
        return "escalate"

    return "execute"