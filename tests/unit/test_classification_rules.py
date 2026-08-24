import pytest

from app.domain.enums.failure_category import FailureCategory
from app.intelligence.classification.rules import classify_failure


@pytest.mark.parametrize(
    ("failure_reason", "expected_category"),
    [
        (
            "bank_timeout",
            FailureCategory.TEMPORARY_FAILURE,
        ),
        (
            "network_error",
            FailureCategory.TEMPORARY_FAILURE,
        ),
        (
            "processing_error",
            FailureCategory.TEMPORARY_FAILURE,
        ),
        (
            "authentication_failed",
            FailureCategory.CUSTOMER_ACTION_REQUIRED,
        ),
        (
            "insufficient_funds",
            FailureCategory.CUSTOMER_ACTION_REQUIRED,
        ),
        (
            "payment_method_declined",
            FailureCategory.CUSTOMER_ACTION_REQUIRED,
        ),
        (
            "inactivity",
            FailureCategory.CHECKOUT_ABANDONMENT,
        ),
        (
            "repeated_attempts",
            FailureCategory.CHECKOUT_ABANDONMENT,
        ),
        (
            "payment_method_switch",
            FailureCategory.CHECKOUT_ABANDONMENT,
        ),
        (
            "invalid_details",
            FailureCategory.PERMANENT_FAILURE,
        ),
        (
            "closed_account",
            FailureCategory.PERMANENT_FAILURE,
        ),
        (
            "blocked_payment",
            FailureCategory.PERMANENT_FAILURE,
        ),
    ],
)
def test_classify_failure(
    failure_reason: str,
    expected_category: FailureCategory,
) -> None:
    result = classify_failure(failure_reason)

    assert result == expected_category


def test_classify_failure_normalizes_input() -> None:
    result = classify_failure(
        "  BANK_TIMEOUT  "
    )

    assert result == FailureCategory.TEMPORARY_FAILURE


def test_classify_failure_rejects_unknown_reason() -> None:
    with pytest.raises(
        ValueError,
        match="Unknown failure reason",
    ):
        classify_failure(
            "unknown_failure"
        )