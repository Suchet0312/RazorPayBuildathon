import logging
import json
from datetime import datetime, timezone
import sys

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add custom fields if they exist
        if hasattr(record, "run_id"):
            log_data["run_id"] = record.run_id
        if hasattr(record, "payment_id"):
            log_data["payment_id"] = record.payment_id
        if hasattr(record, "workflow_status"):
            log_data["workflow_status"] = record.workflow_status
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger

class RecoveryLogger:
    def __init__(self, run_id: str = None, payment_id: str = None):
        self.logger = logging.getLogger("recovery_brain")
        self.extra = {}
        if run_id:
            self.extra["run_id"] = run_id
        if payment_id:
            self.extra["payment_id"] = payment_id
            
    def info(self, msg, **kwargs):
        extra = {**self.extra, **kwargs}
        self.logger.info(msg, extra=extra)
        
    def error(self, msg, **kwargs):
        extra = {**self.extra, **kwargs}
        self.logger.error(msg, extra=extra)
        
    def warning(self, msg, **kwargs):
        extra = {**self.extra, **kwargs}
        self.logger.warning(msg, extra=extra)
