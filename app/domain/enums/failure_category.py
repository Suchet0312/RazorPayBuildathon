from enum import Enum


class FailureCategory(str, Enum):
    TEMPORARY_FAILURE = "temporary_failure"
    CUSTOMER_ACTION_REQUIRED = "customer_action_required"
    CHECKOUT_ABANDONMENT = "checkout_abandonment"
    PERMANENT_FAILURE = "permanent_failure"