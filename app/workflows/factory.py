from app.domain.models.payment import PaymentRiskRecord
from app.workflows.state import RecoveryState


def create_recovery_state(
    run_id: str,
    payment: PaymentRiskRecord,
) -> RecoveryState:
    return {
        "run_id": run_id,
        "payment": payment,
        "audit_trail": [],
        "errors": [],
        "recovered_amount": 0.0,
        "policy_approved": False,
    }