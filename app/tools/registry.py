import os

from app.domain.enums.recovery_action import RecoveryAction
from app.tools.alternate_method_tool import MockAlternateMethodTool
from app.tools.b2b_receivables_tool import B2BReceivablesChaser
from app.tools.base import RecoveryTool
from app.tools.hinglish_voice_tool import HinglishVoiceRecoveryTool
from app.tools.mandate_retry_tool import MandateRetryTool
from app.tools.promise_to_pay_tool import PromiseToPayTool
from app.tools.recovery_link_tool import MockRecoveryLinkTool, RazorpayRecoveryLinkTool
from app.tools.retry_tool import MockRetryTool, RazorpayRetryTool


class ToolRegistry:
    """
    Maps approved recovery actions to execution tools.

    Uses real Razorpay API tools when credentials are configured,
    otherwise falls back to mock implementations automatically.
    """

    def __init__(self) -> None:
        use_razorpay = bool(
            os.getenv("RAZORPAY_KEY_ID") and os.getenv("RAZORPAY_KEY_SECRET")
        )

        retry_tool: RecoveryTool = RazorpayRetryTool() if use_razorpay else MockRetryTool()
        recovery_link_tool: RecoveryTool = (
            RazorpayRecoveryLinkTool() if use_razorpay else MockRecoveryLinkTool()
        )

        self._tools: dict[RecoveryAction, RecoveryTool] = {
            # Core retry actions
            RecoveryAction.RETRY_NOW: retry_tool,
            RecoveryAction.RETRY_LATER: retry_tool,
            # Customer contact / checkout recovery
            RecoveryAction.SEND_RECOVERY_LINK: recovery_link_tool,
            # Alternative payment method suggestion
            RecoveryAction.SUGGEST_ALTERNATE_METHOD: MockAlternateMethodTool(),
            # Mandate / subscription sequencer
            RecoveryAction.MANDATE_RETRY: MandateRetryTool(),
            # B2B receivables chaser
            RecoveryAction.B2B_RECEIVABLES_CHASE: B2BReceivablesChaser(),
            # Promise-to-pay commitment tracker
            RecoveryAction.PROMISE_TO_PAY: PromiseToPayTool(),
            # Hinglish voice / SMS recovery
            RecoveryAction.HINGLISH_VOICE_RECOVERY: HinglishVoiceRecoveryTool(),
        }

    def get_tool(self, action: RecoveryAction) -> RecoveryTool | None:
        return self._tools.get(action)

    def registered_actions(self) -> list[str]:
        return [a.value for a in self._tools]
