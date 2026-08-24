from app.domain.enums.failure_category import FailureCategory


FAILURE_REASON_MAPPING = {
    "bank_timeout": FailureCategory.TEMPORARY_FAILURE,
    "network_error": FailureCategory.TEMPORARY_FAILURE,
    "processing_error": FailureCategory.TEMPORARY_FAILURE,

    "authentication_failed": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "insufficient_funds": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "payment_method_declined": FailureCategory.CUSTOMER_ACTION_REQUIRED,

    "inactivity": FailureCategory.CHECKOUT_ABANDONMENT,
    "repeated_attempts": FailureCategory.CHECKOUT_ABANDONMENT,
    "payment_method_switch": FailureCategory.CHECKOUT_ABANDONMENT,

    "invalid_details": FailureCategory.PERMANENT_FAILURE,
    "closed_account": FailureCategory.PERMANENT_FAILURE,
    "blocked_payment": FailureCategory.PERMANENT_FAILURE,
}


def classify_failure(
    failure_reason: str,
) -> FailureCategory:
    """
    Deterministically classify a payment failure reason.

    Raises:
        ValueError: If the failure reason is unknown.
    """

    normalized_reason = (
        failure_reason.strip().lower()
    )

    if normalized_reason not in FAILURE_REASON_MAPPING:
        raise ValueError(
            f"Unknown failure reason: {failure_reason}"
        )

    return FAILURE_REASON_MAPPING[
        normalized_reason
    ]