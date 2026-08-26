from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from app.core.database import Base
from datetime import datetime, timezone

class RunRecord(Base):
    __tablename__ = "workflow_runs"

    run_id = Column(String, primary_key=True, index=True)
    payment_id = Column(String, index=True)
    workflow_status = Column(String)
    recovered_amount = Column(Float, default=0.0)
    state_snapshot = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditRecord(Base):
    __tablename__ = "audit_trails"

    audit_id = Column(String, primary_key=True, index=True)
    run_id = Column(String, index=True)
    payment_id = Column(String, index=True)
    timestamp = Column(DateTime)
    stage = Column(String)
    input_summary = Column(Text)
    decision = Column(String)
    reason_codes = Column(JSON) # JSON column for list of strings
    actor = Column(String)
    result = Column(String)
    metadata_json = Column(JSON) # Storing metadata as JSON
