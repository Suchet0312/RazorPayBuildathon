from datetime import datetime

from app.agents.diagnosis_agent import diagnose_payment
from app.domain.enums.failure_category import FailureCategory
from app.domain.enums.payment_status import PaymentStatus
from app.domain.models.payment import PaymentRiskRecord


def create_test_payment(
    attempt_count: int = 1,
    customer_success_rate: float = 0.90,
    previous_retry_success_rate: float = 0.80,
) -> PaymentRiskRecord:
    return PaymentRiskRecord(
        payment_id="pay_test_001",
        customer_id="cust_test_001",
        merchant_id="merchant_test_001",
        amount=5000.0,
        currency="INR",
        payment_method="upi",
        status=PaymentStatus.FAILED,
        failure_reason="bank_timeout",
        attempt_count=attempt_count,
        event_timestamp=datetime.now(),
        customer_success_rate=customer_success_rate,
        previous_retry_success_rate=previous_retry_success_rate,
        contact_count=0,
    )


def test_diagnosis_for_temporary_high_probability_failure():
    payment = create_test_payment()

    diagnosis = diagnose_payment(
        payment=payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.82,
    )

    assert diagnosis.confidence >= 0.0
    assert diagnosis.confidence <= 1.0

    assert "TEMPORARY_FAILURE" in diagnosis.reason_codes
    assert "HIGH_RECOVERY_PROBABILITY" in diagnosis.reason_codes
    assert "STRONG_CUSTOMER_HISTORY" in diagnosis.reason_codes

    assert len(diagnosis.summary) > 0


def test_diagnosis_for_permanent_failure():
    payment = create_test_payment(
        customer_success_rate=0.30,
        previous_retry_success_rate=0.20,
    )

    diagnosis = diagnose_payment(
        payment=payment,
        failure_category=FailureCategory.PERMANENT_FAILURE,
        recovery_probability=0.15,
    )

    assert "PERMANENT_FAILURE" in diagnosis.reason_codes
    assert "LOW_RECOVERY_PROBABILITY" in diagnosis.reason_codes
    assert "WEAK_CUSTOMER_HISTORY" in diagnosis.reason_codes


def test_diagnosis_for_repeated_attempts():
    payment = create_test_payment(attempt_count=3)

    diagnosis = diagnose_payment(
        payment=payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.60,
    )

    assert "REPEATED_ATTEMPTS" in diagnosis.reason_codes
    assert "MODERATE_RECOVERY_PROBABILITY" in diagnosis.reason_codes


def test_diagnosis_confidence_is_bounded():
    payment = create_test_payment()

    diagnosis = diagnose_payment(
        payment=payment,
        failure_category=FailureCategory.TEMPORARY_FAILURE,
        recovery_probability=0.99,
    )

    assert 0.0 <= diagnosis.confidence <= 1.0
