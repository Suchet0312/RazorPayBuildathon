from app.domain.enums.recovery_action import RecoveryAction
from app.tools.alternate_method_tool import MockAlternateMethodTool
from app.tools.base import RecoveryTool
from app.tools.recovery_link_tool import MockRecoveryLinkTool
from app.tools.retry_tool import MockRetryTool


class ToolRegistry:
    """
    Maps approved recovery actions to execution tools.

    The registry provides capability lookup only.
    It does not evaluate policy or approve actions.
    """

    def __init__(self) -> None:
        retry_tool = MockRetryTool()
        recovery_link_tool = MockRecoveryLinkTool()
        alternate_method_tool = MockAlternateMethodTool()

        self._tools: dict[
            RecoveryAction,
            RecoveryTool,
        ] = {
            RecoveryAction.RETRY_NOW: retry_tool,
            RecoveryAction.RETRY_LATER: retry_tool,
            RecoveryAction.SEND_RECOVERY_LINK: recovery_link_tool,
            RecoveryAction.SUGGEST_ALTERNATE_METHOD: (
                alternate_method_tool
            ),
        }

    def get_tool(
        self,
        action: RecoveryAction,
    ) -> RecoveryTool | None:
        return self._tools.get(action)