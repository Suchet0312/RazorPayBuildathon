from typing import Annotated, TypedDict

from app.domain.models.audit import AuditEvent
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import (
    Diagnosis,
    ExecutionResult,
    PolicyDecision,
    RecoveryPlan,
    VerificationResult,
)


def merge_audit_trail(
    existing: list[AuditEvent],
    new: list[AuditEvent],
) -> list[AuditEvent]:
    """
    Accumulate audit events across workflow nodes.
    """

    return existing + new


class RecoveryState(TypedDict, total=False):
    # Workflow identity
    run_id: str

    # Original payment
    payment: PaymentRiskRecord

    # Classification
    classification: str
    failure_category: str

    # ML prediction
    recovery_probability: float
    expected_recovery_value: float
    priority_score: float

    # Agent outputs
    diagnosis: Diagnosis
    recovery_plan: RecoveryPlan

    # Policy decision
    policy_decision: PolicyDecision
    policy_approved: bool

    # Execution and verification
    execution_result: ExecutionResult
    verification_result: VerificationResult

    # Workflow terminal status
    workflow_status: str
    recovered_amount: float

    # Audit and errors
    audit_trail: Annotated[
        list[AuditEvent],
        merge_audit_trail,
    ]

    errors: list[str]