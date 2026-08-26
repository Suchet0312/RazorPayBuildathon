from app.domain.enums.failure_category import FailureCategory


FAILURE_REASON_MAPPING = {
    # Temporary failures – transient issues that may self-resolve
    "bank_timeout": FailureCategory.TEMPORARY_FAILURE,
    "network_error": FailureCategory.TEMPORARY_FAILURE,
    "processing_error": FailureCategory.TEMPORARY_FAILURE,
    "gateway_timeout": FailureCategory.TEMPORARY_FAILURE,
    "issuer_timeout": FailureCategory.TEMPORARY_FAILURE,
    "payment_gateway_error": FailureCategory.TEMPORARY_FAILURE,
    "acquirer_error": FailureCategory.TEMPORARY_FAILURE,
    "server_error": FailureCategory.TEMPORARY_FAILURE,
    "technical_error": FailureCategory.TEMPORARY_FAILURE,

    # Customer action required – customer must intervene
    "authentication_failed": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "insufficient_funds": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "payment_method_declined": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "card_expired": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "cvv_mismatch": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "3ds_failed": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "otp_expired": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "low_balance": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "upi_pin_incorrect": FailureCategory.CUSTOMER_ACTION_REQUIRED,

    # Checkout abandonment – user dropped off before completing
    "inactivity": FailureCategory.CHECKOUT_ABANDONMENT,
    "repeated_attempts": FailureCategory.CHECKOUT_ABANDONMENT,
    "payment_method_switch": FailureCategory.CHECKOUT_ABANDONMENT,
    "session_expired": FailureCategory.CHECKOUT_ABANDONMENT,
    "cart_abandoned": FailureCategory.CHECKOUT_ABANDONMENT,
    "page_closed": FailureCategory.CHECKOUT_ABANDONMENT,
    "checkout_timeout": FailureCategory.CHECKOUT_ABANDONMENT,

    # Permanent failures – unlikely to recover automatically
    "invalid_details": FailureCategory.PERMANENT_FAILURE,
    "closed_account": FailureCategory.PERMANENT_FAILURE,
    "blocked_payment": FailureCategory.PERMANENT_FAILURE,
    "fraud_detected": FailureCategory.PERMANENT_FAILURE,
    "card_blocked": FailureCategory.PERMANENT_FAILURE,
    "account_frozen": FailureCategory.PERMANENT_FAILURE,
    "chargeback": FailureCategory.PERMANENT_FAILURE,

    # Subscription / recurring failure reasons
    "subscription_failed": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "subscription_cancelled": FailureCategory.PERMANENT_FAILURE,
    "subscription_expired": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "plan_limit_exceeded": FailureCategory.CUSTOMER_ACTION_REQUIRED,

    # Mandate / ECS / NACH specific
    "mandate_rejected": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "mandate_expired": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "mandate_revoked": FailureCategory.PERMANENT_FAILURE,
    "nach_bounce": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "ecs_bounce": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "debit_failed": FailureCategory.TEMPORARY_FAILURE,

    # B2B / invoice / receivables
    "invoice_overdue": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "b2b_overdue": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "payment_promised": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "credit_limit_exceeded": FailureCategory.CUSTOMER_ACTION_REQUIRED,
    "invoice_disputed": FailureCategory.PERMANENT_FAILURE,
}


def classify_failure(
    failure_reason: str | None,
) -> FailureCategory:
    """
    Deterministically classify a payment failure reason.

    Returns TEMPORARY_FAILURE as a safe default for unknown or missing
    failure reasons rather than crashing the workflow. Unknown reasons
    are treated as potentially recoverable transient issues.
    """

    if failure_reason is None:
        return FailureCategory.TEMPORARY_FAILURE

    normalized_reason = failure_reason.strip().lower()

    if not normalized_reason:
        return FailureCategory.TEMPORARY_FAILURE

    return FAILURE_REASON_MAPPING.get(
        normalized_reason,
        FailureCategory.TEMPORARY_FAILURE,  # safe default — don't crash
    )
