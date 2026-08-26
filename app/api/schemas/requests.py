from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.enums.payment_status import PaymentStatus


class RecoveryAnalyzeRequest(BaseModel):
    payment_id: str = Field(min_length=1, description="Unique payment identifier")
    customer_id: str = Field(min_length=1, description="Unique customer identifier")
    merchant_id: str = Field(min_length=1, description="Unique merchant identifier")
    amount: float = Field(gt=0, description="Payment amount")
    currency: str = Field(default="INR", min_length=3, max_length=3)
    payment_method: str = Field(min_length=1)
    status: PaymentStatus
    failure_reason: str | None = None
    attempt_count: int = Field(ge=0, default=0)
    event_timestamp: datetime
    customer_success_rate: float = Field(ge=0.0, le=1.0)
    previous_retry_success_rate: float = Field(ge=0.0, le=1.0)
    contact_count: int = Field(ge=0, default=0)


class BatchAnalyzeRequest(BaseModel):
    """Batch of payments to run through the recovery workflow."""
    payments: list[RecoveryAnalyzeRequest] = Field(
        min_length=1,
        max_length=100,
        description="List of payments to analyse (max 100 per batch)",
    )
    stop_on_error: bool = Field(
        default=False,
        description="If True, abort the batch on the first error",
    )


class PromiseToPayRequest(BaseModel):
    """Record a customer's payment commitment."""
    payment_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    merchant_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    commitment_window_days: int = Field(default=3, ge=1, le=30)
    follow_up_enabled: bool = True
    notes: str | None = None


class HinglishRecoveryRequest(BaseModel):
    """Trigger a Hinglish voice/SMS recovery nudge for a payment."""
    payment_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    merchant_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    failure_reason: str | None = None
    channel: str = Field(
        default="sms",
        description="Delivery channel: sms | voice | whatsapp",
    )
