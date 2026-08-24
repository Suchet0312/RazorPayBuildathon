from enum import Enum


class RecoveryAction(str, Enum):
    RETRY_NOW = "retry_now"
    RETRY_LATER = "retry_later"
    SEND_RECOVERY_LINK = "send_recovery_link"
    SUGGEST_ALTERNATE_METHOD = "suggest_alternate_method"
    ESCALATE_TO_MERCHANT = "escalate_to_merchant"
    DO_NOTHING = "do_nothing"