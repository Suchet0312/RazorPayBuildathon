from app.domain.services import (
    normalize_payment_record,
    validate_payment_record,
)
from app.workflows.factory import create_recovery_state


sample_payment = {
    "payment_id": "pay_001",
    "customer_id": "cust_001",
    "merchant_id": "merchant_001",
    "amount": 5000.0,
    "currency": "inr",
    "payment_method": "UPI",
    "status": "failed",
    "failure_reason": " BANK_TIMEOUT ",
    "attempt_count": 1,
    "event_timestamp": "2026-08-24T20:00:00",
    "customer_success_rate": 0.90,
    "previous_retry_success_rate": 0.75,
    "contact_count": 0,
}


payment = validate_payment_record(sample_payment)

normalized_payment = normalize_payment_record(payment)

state = create_recovery_state(
    run_id="run_001",
    payment=normalized_payment,
)

print("VALIDATED PAYMENT:")
print(normalized_payment.model_dump())

print("\nINITIAL RECOVERY STATE:")
print(state)