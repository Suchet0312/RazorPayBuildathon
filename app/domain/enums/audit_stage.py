from enum import Enum


class AuditStage(str, Enum):
    INGEST = "ingest"
    CLASSIFICATION = "classification"
    PREDICTION = "prediction"
    DIAGNOSIS = "diagnosis"
    PLANNING = "planning"
    POLICY_GATE = "policy_gate"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    AUDIT = "audit"