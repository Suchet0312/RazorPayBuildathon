from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums.recovery_action import RecoveryAction


class Diagnosis(BaseModel):
    summary: str = Field(
        min_length=1,
        description="Human-readable explanation of the payment issue",
    )

    reason_codes: list[str] = Field(
        default_factory=list,
        description="Structured reasons supporting the diagnosis",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the diagnosis",
    )


class RecoveryPlan(BaseModel):
    action: RecoveryAction

    action_parameters: dict[str, Any] = Field(
        default_factory=dict,
    )

    reason_codes: list[str] = Field(
        default_factory=list,
    )

    expected_recovery_value: float = Field(
        ge=0.0,
    )

    priority_score: float = Field(
        ge=0.0,
    )


class PolicyDecision(BaseModel):
    approved: bool

    reason_codes: list[str] = Field(
        default_factory=list,
    )

    reason: str = Field(
        min_length=1,
    )


class ExecutionRequest(BaseModel):
    """
    Controlled request passed from the workflow
    to an approved recovery execution tool.
    """

    run_id: str = Field(
        min_length=1,
    )

    payment_id: str = Field(
        min_length=1,
    )

    action: RecoveryAction

    action_parameters: dict[str, Any] = Field(
        default_factory=dict,
    )


class ExecutionResult(BaseModel):
    success: bool

    action: RecoveryAction

    external_reference_id: str | None = None

    message: str = Field(
        min_length=1,
    )

    error_code: str | None = None


class VerificationResult(BaseModel):
    verified: bool

    recovered_amount: float = Field(
        ge=0.0,
        default=0.0,
    )

    message: str = Field(
        min_length=1,
    )