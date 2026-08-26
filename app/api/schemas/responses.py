from typing import Any
from pydantic import BaseModel


class RecoveryAnalyzeResponse(BaseModel):
    run_id: str | None = None
    classification: str | None = None
    recovery_probability: float | None = None
    recovery_plan: Any | None = None
    policy_decision: Any | None = None
    execution_result: Any | None = None
    verification_result: Any | None = None
    workflow_status: str | None = None
    recovered_amount: float | None = None
    errors: list[str] | None = None
    message: str | None = None


class RecoveryStatusResponse(BaseModel):
    run_id: str
    payment_id: str
    workflow_status: str
    recovered_amount: float
    audit_trail: list[Any] = []


class BatchPaymentResult(BaseModel):
    """Per-payment result within a batch response."""
    payment_id: str
    run_id: str | None = None
    workflow_status: str | None = None
    recovery_probability: float | None = None
    recommended_action: str | None = None
    policy_approved: bool | None = None
    recovered_amount: float | None = None
    error: str | None = None


class BatchAnalyzeResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    total_revenue_at_risk: float
    total_predicted_recoverable: float
    total_actually_recovered: float
    results: list[BatchPaymentResult]


class PromiseToPayResponse(BaseModel):
    reference_id: str
    payment_id: str
    customer_id: str
    commitment_deadline: str
    follow_up_times: list[str]
    message: str
    metadata: dict[str, Any] = {}


class HinglishRecoveryResponse(BaseModel):
    reference_id: str
    payment_id: str
    channel: str
    message_sent: str
    dispatched_at: str
    metadata: dict[str, Any] = {}
