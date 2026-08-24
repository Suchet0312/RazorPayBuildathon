from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums.audit_stage import AuditStage


class AuditEvent(BaseModel):
    audit_id: str = Field(
        min_length=1,
        description="Unique audit event identifier",
    )

    run_id: str = Field(
        min_length=1,
        description="Recovery workflow run identifier",
    )

    payment_id: str = Field(
        min_length=1,
        description="Payment associated with this event",
    )

    timestamp: datetime

    stage: AuditStage

    input_summary: str = Field(
        min_length=1,
    )

    decision: str = Field(
        min_length=1,
    )

    reason_codes: list[str] = Field(
        default_factory=list,
    )

    actor: str = Field(
        min_length=1,
        description="Component responsible for this event",
    )

    result: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )