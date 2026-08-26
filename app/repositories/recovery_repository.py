from sqlalchemy.orm import Session
from app.data.models import RunRecord, AuditRecord
from app.workflows.state import RecoveryState
import json
from datetime import datetime, date

def _serialize(obj):
    if hasattr(obj, "model_dump_json"):
        return json.loads(obj.model_dump_json())
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, "value"):
        return obj.value
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)

class RecoveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_run(self, state: RecoveryState):
        state_dict = {}
        for k, v in state.items():
            if k == "audit_trail":
                continue
            state_dict[k] = _serialize(v)

        run_record = RunRecord(
            run_id=state.get("run_id"),
            payment_id=state["payment"].payment_id if "payment" in state else "unknown",
            workflow_status=state.get("workflow_status"),
            recovered_amount=state.get("recovered_amount", 0.0),
            state_snapshot=state_dict
        )
        self.db.merge(run_record)

        audit_trail = state.get("audit_trail", [])
        for audit in audit_trail:
            audit_record = AuditRecord(
                audit_id=audit.audit_id,
                run_id=audit.run_id,
                payment_id=audit.payment_id,
                timestamp=audit.timestamp,
                stage=audit.stage.value,
                input_summary=audit.input_summary,
                decision=audit.decision,
                reason_codes=audit.reason_codes,
                actor=audit.actor,
                result=audit.result,
                metadata_json=audit.metadata
            )
            self.db.merge(audit_record)

        self.db.commit()

    def get_run_status(self, run_id: str) -> dict | None:
        run = self.db.query(RunRecord).filter(RunRecord.run_id == run_id).first()
        if not run:
            return None
        
        audits = self.db.query(AuditRecord).filter(AuditRecord.run_id == run_id).order_by(AuditRecord.timestamp).all()
        
        audit_trail = [
            {
                "audit_id": a.audit_id,
                "stage": a.stage,
                "input_summary": a.input_summary,
                "decision": a.decision,
                "reason_codes": a.reason_codes,
                "actor": a.actor,
                "result": a.result,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "metadata": a.metadata_json
            } for a in audits
        ]
        
        return {
            "run_id": run.run_id,
            "payment_id": run.payment_id,
            "workflow_status": run.workflow_status,
            "recovered_amount": run.recovered_amount,
            "audit_trail": audit_trail
        }

