from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_metrics_endpoint():
    response = client.get("/api/v1/metrics/performance")
    assert response.status_code == 200
    data = response.json()
    assert "roc_auc" in data
    assert "ece_calibrated" in data
    assert "dataset_type" in data
    assert data["roc_auc"] > 0.50

def test_risk_evaluate_flow():
    payload = {
        "user_id": "usr_99812",
        "merchant_id": "mer_4410",
        "amount": 45.0,
        "currency": "USD",
        "payment_method": "CREDIT_CARD",
        "device_fingerprint": "dev_mac_8819ab",
        "ip_address": "127.0.0.1",
        "geo_location": "US-NY"
    }
    response = client.post("/api/v1/risk/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "recommended_action" in data
    assert "explanations" in data
    assert len(data["explanations"]) > 0

def test_policies_endpoint():
    response = client.get("/api/v1/policies")
    assert response.status_code == 200
    policies = response.json()
    assert len(policies) > 0
