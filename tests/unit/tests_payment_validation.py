import pytest
from pydantic import ValidationError

from app.domain.services import validate_payment_record


def get_valid_payment():
    return {
        "payment_id": "pay_001",
        "customer_id": "cust_001",
        "merchant_id": "merchant_001",
        "amount": 5000.0,
        "currency": "INR",
        "payment_method": "upi",
        "status": "failed",
        "failure_reason": "bank_timeout",
        "attempt_count": 1,
        "event_timestamp": "2026-08-24T20:00:00",
        "customer_success_rate": 0.90,
        "previous_retry_success_rate": 0.75,
        "contact_count": 0,
    }


def test_valid_payment():
    payment = validate_payment_record(get_valid_payment())

    assert payment.payment_id == "pay_001"
    assert payment.amount == 5000.0


def test_negative_amount_fails():
    data = get_valid_payment()
    data["amount"] = -500

    with pytest.raises(ValidationError):
        validate_payment_record(data)


def test_invalid_success_rate_fails():
    data = get_valid_payment()
    data["customer_success_rate"] = 1.5

    with pytest.raises(ValidationError):
        validate_payment_record(data)


def test_negative_contact_count_fails():
    data = get_valid_payment()
    data["contact_count"] = -1

    with pytest.raises(ValidationError):
        validate_payment_record(data)