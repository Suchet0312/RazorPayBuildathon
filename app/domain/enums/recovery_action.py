from enum import Enum


class RecoveryAction(str, Enum):
    RETRY_NOW = "retry_now"
    RETRY_LATER = "retry_later"
    SEND_RECOVERY_LINK = "send_recovery_link"
    SUGGEST_ALTERNATE_METHOD = "suggest_alternate_method"
    ESCALATE_TO_MERCHANT = "escalate_to_merchant"
    DO_NOTHING = "do_nothing"
    # New actions covering all image scenarios
    MANDATE_RETRY = "mandate_retry"
    PROMISE_TO_PAY = "promise_to_pay"
    B2B_RECEIVABLES_CHASE = "b2b_receivables_chase"
    HINGLISH_VOICE_RECOVERY = "hinglish_voice_recovery"
