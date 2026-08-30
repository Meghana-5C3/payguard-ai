import sys
import os
import uuid
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

class TestAllEndpointsAudit(unittest.TestCase):

    def test_01_root(self):
        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "HEALTHY")
        print("[PASS] Endpoint GET / passed")

    def test_02_scenario_normal(self):
        payload = {
            "user_id": f"usr_audit_{uuid.uuid4().hex[:6]}",
            "merchant_id": "mer_4410",
            "amount": 45.50,
            "currency": "USD",
            "payment_method": "CREDIT_CARD",
            "device_fingerprint": "dev_mac_8819ab",
            "ip_address": "192.168.1.105",
            "geo_location": "US-NY"
        }
        res = client.post("/api/v1/risk/evaluate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("risk_score", data)
        self.assertEqual(data["recommended_action"], "APPROVE")
        self.assertGreater(len(data["explanations"]), 0)
        print(f"[PASS] Scenario 1 (Normal Coffee): Score={data['risk_score']}, Action={data['recommended_action']}")

    def test_03_scenario_ato_proxy(self):
        payload = {
            "user_id": f"usr_audit_{uuid.uuid4().hex[:6]}",
            "merchant_id": "mer_9950",
            "amount": 1850.00,
            "currency": "USD",
            "payment_method": "CREDIT_CARD",
            "device_fingerprint": "dev_unknown_xyz99",
            "ip_address": "185.220.101.5", # Proxy IP (92.0 risk)
            "geo_location": "US-NY"
        }
        res = client.post("/api/v1/risk/evaluate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("risk_score", data)
        self.assertIn(data["recommended_action"], ["APPROVE", "VERIFY", "HOLD"])
        print(f"[PASS] Scenario 2 (ATO Proxy): Score={data['risk_score']}, Action={data['recommended_action']}")

    def test_04_scenario_high_amount_and_analyst_override(self):
        payload = {
            "user_id": f"usr_audit_{uuid.uuid4().hex[:6]}",
            "merchant_id": "mer_9950",
            "amount": 8500.00,
            "currency": "USD",
            "payment_method": "CREDIT_CARD",
            "device_fingerprint": "dev_hacker_9901",
            "ip_address": "109.70.100.12",
            "geo_location": "CA-ON"
        }
        res = client.post("/api/v1/risk/evaluate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("risk_score", data)
        print(f"[PASS] Scenario 3 (Whale Transfer): Score={data['risk_score']}, Action={data['recommended_action']}")

        # Fetch analyst queue
        q_res = client.get("/api/v1/analyst/queue?status_filter=ALL")
        self.assertEqual(q_res.status_code, 200)
        queue = q_res.json()
        self.assertGreater(len(queue), 0)
        eval_item = queue[0]
        print(f"[PASS] Analyst Queue fetch: {len(queue)} total item(s) found.")

        # Submit manual analyst override
        o_res = client.post("/api/v1/analyst/override", json={
            "evaluation_id": eval_item["evaluation_id"],
            "override_action": "REJECT",
            "reason_code": "SUSPECTED_FRAUD_RING",
            "analyst_notes": "Confirmed IP address matched TOR exit node database."
        })
        self.assertEqual(o_res.status_code, 200)
        o_data = o_res.json()
        self.assertEqual(o_data["final_action"], "REJECT")
        print("[PASS] Analyst manual override submission successful!")

    def test_05_policies_and_metrics(self):
        p_res = client.get("/api/v1/policies")
        self.assertEqual(p_res.status_code, 200)
        self.assertGreater(len(p_res.json()), 0)
        print("[PASS] Policies GET endpoint verified.")

        m_res = client.get("/api/v1/metrics/performance")
        self.assertEqual(m_res.status_code, 200)
        m_data = m_res.json()
        self.assertIn("roc_auc", m_data)
        self.assertIn("ece_calibrated", m_data)
        print(f"[PASS] Metrics GET endpoint verified (ROC-AUC={m_data['roc_auc']}, ECE={m_data['ece_calibrated']}).")

        a_res = client.get("/api/v1/audit/logs")
        self.assertEqual(a_res.status_code, 200)
        self.assertGreater(len(a_res.json()), 0)
        print(f"[PASS] Audit Logs GET endpoint verified ({len(a_res.json())} logs found).")

if __name__ == "__main__":
    unittest.main()
