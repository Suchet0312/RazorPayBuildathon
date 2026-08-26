from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class DashboardMetricsResponse(BaseModel):
    total_processed: int
    revenue_at_risk: float
    predicted_recoverable: float
    actually_recovered: float
    recovery_rate: float
    actions_approved: int
    actions_blocked: int
    unresolved_exceptions: int

class BatchRecordSummary(BaseModel):
    run_id: str
    payment_id: str
    amount: float
    failure_category: str
    recovery_probability: float
    expected_recovery_value: float
    recommended_action: str
    policy_decision: str
    execution_status: str
    verification_status: str
    recovered_amount: float
    workflow_status: str
    timestamp: Optional[datetime]

class PaymentDrillDownResponse(BaseModel):
    payment_info: dict
    intelligence: dict
    diagnosis: dict
    recovery_plan: dict
    policy_guardian: dict
    execution: dict
    audit_trail: List[dict]
    workflow_status: str

class FailureDemoResponse(BaseModel):
    status: str
    message: str
    run_id: str
    audit_trail: List[dict]
