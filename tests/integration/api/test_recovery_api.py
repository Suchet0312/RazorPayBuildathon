from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app.main import app
from app.domain.enums.payment_status import PaymentStatus

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_recovery_analyze_endpoint_valid_request():
    request_data = {
        "payment_id": "pay_test123",
        "customer_id": "cust_test123",
        "merchant_id": "merch_test123",
        "amount": 5000.0,
        "currency": "INR",
        "payment_method": "upi",
        "status": PaymentStatus.FAILED.value,
        "failure_reason": "insufficient_funds",
        "attempt_count": 1,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "customer_success_rate": 0.9,
        "previous_retry_success_rate": 0.5,
        "contact_count": 0
    }

    response = client.post("/recovery/analyze", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert "workflow_status" in data
    assert data["workflow_status"] is not None

def test_recovery_analyze_endpoint_invalid_request():
    request_data = {
        "payment_id": "pay_test123",
        # Missing required fields like customer_id, merchant_id, etc.
    }
    
    response = client.post("/recovery/analyze", json=request_data)
    assert response.status_code == 422 # Validation error

from unittest.mock import patch

def test_recovery_analyze_internal_error():
    request_data = {
        "payment_id": "pay_test123",
        "customer_id": "cust_test123",
        "merchant_id": "merch_test123",
        "amount": 5000.0,
        "currency": "INR",
        "payment_method": "upi",
        "status": PaymentStatus.FAILED.value,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "customer_success_rate": 0.9,
        "previous_retry_success_rate": 0.5,
    }
    with patch("app.services.recovery_service.RecoveryService.analyze_payment_async", side_effect=Exception("Database down")):
        response = client.post("/recovery/analyze", json=request_data)
        assert response.status_code == 500

def test_recovery_status_endpoint():
    with patch("app.services.recovery_service.RecoveryService.get_status") as mock_get_status:
        mock_get_status.return_value = {
            "run_id": "run_123",
            "payment_id": "pay_123",
            "workflow_status": "COMPLETED",
            "recovered_amount": 5000.0,
            "audit_trail": []
        }
        response = client.get("/recovery/status/run_123")
        assert response.status_code == 200
        assert response.json()["workflow_status"] == "COMPLETED"
