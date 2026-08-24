from app.domain.models.payment import PaymentRiskRecord


def validate_payment_record(data: dict) -> PaymentRiskRecord:
    return PaymentRiskRecord.model_validate(data)


def normalize_payment_record(
    payment: PaymentRiskRecord,
) -> PaymentRiskRecord:
    return payment.model_copy(
        update={
            "currency": payment.currency.upper(),
            "payment_method": payment.payment_method.lower(),
            "failure_reason": (
                payment.failure_reason.lower()
                if payment.failure_reason
                else None
            ),
        }
    )