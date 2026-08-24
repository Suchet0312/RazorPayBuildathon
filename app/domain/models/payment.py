from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.enums.payment_status import PaymentStatus


class PaymentRiskRecord(BaseModel):
    payment_id: str = Field(
        min_length=1,
        description="Unique payment identifier",
    )

    customer_id: str = Field(
        min_length=1,
        description="Unique customer identifier",
    )

    merchant_id: str = Field(
        min_length=1,
        description="Unique merchant identifier",
    )

    amount: float = Field(
        gt=0,
        description="Payment amount",
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    payment_method: str = Field(
        min_length=1,
    )

    status: PaymentStatus

    failure_reason: str | None = None

    attempt_count: int = Field(
        ge=0,
        default=0,
    )

    event_timestamp: datetime

    customer_success_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    previous_retry_success_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    contact_count: int = Field(
        ge=0,
        default=0,
    )

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator(
        "payment_id",
        "customer_id",
        "merchant_id",
        "payment_method",
    )
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value

    @field_validator("failure_reason")
    @classmethod
    def normalize_failure_reason(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip().lower()

        return value or None