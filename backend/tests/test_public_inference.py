import os
import sys
import json
import unittest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.main import app
from backend.app.ml.public_inference import PublicInferenceService, PUBLIC_FEATURE_NAMES

client = TestClient(app)

class TestPublicInference(unittest.TestCase):

    def setUp(self):
        self.service = PublicInferenceService()
        self.sample_payload = {col: 0.0 for col in PUBLIC_FEATURE_NAMES}
        self.sample_payload["Amount"] = 149.99
        self.sample_payload["V4"] = 2.5
        self.sample_payload["V14"] = -3.5

        # Synthetic artifacts directory for isolation testing
        self.synthetic_artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts"))

    def test_01_to_06_components_and_metadata_loaded(self):
        self.assertIsNotNone(self.service.model)
        self.assertIsNotNone(self.service.preprocessor)
        self.assertIsNotNone(self.service.calibrator)
        self.assertEqual(len(self.service.feature_columns), 30)
        self.assertIn("V1", self.service.feature_columns)
        self.assertIn("Amount", self.service.feature_columns)

    def test_07_to_15_prediction_and_fields(self):
        res = self.service.predict(self.sample_payload)

        self.assertIn("raw_probability", res)
        self.assertIn("calibrated_probability", res)
        self.assertIn("decision", res)

        self.assertTrue(0.0 <= res["raw_probability"] <= 1.0)
        self.assertTrue(0.0 <= res["calibrated_probability"] <= 1.0)
        self.assertIn(res["decision"], ["LEGITIMATE", "FRAUD"])

        self.assertEqual(res["threshold"], 0.5)
        self.assertEqual(res["threshold_source"], "fixed_default_0.5")
        self.assertEqual(res["model_version"], "v1.0.0")
        self.assertEqual(res["dataset_source"], "public")
        self.assertEqual(res["calibration_method"], "isotonic")

    def test_16_to_18_no_fitting_during_inference(self):
        model_path = os.path.join(self.service.artifacts_dir, "model.joblib")
        calib_path = os.path.join(self.service.artifacts_dir, "calibrator.joblib")

        mtime_model_before = os.path.getmtime(model_path)
        mtime_calib_before = os.path.getmtime(calib_path)

        self.service.predict(self.sample_payload)

        mtime_model_after = os.path.getmtime(model_path)
        mtime_calib_after = os.path.getmtime(calib_path)

        self.assertEqual(mtime_model_before, mtime_model_after)
        self.assertEqual(mtime_calib_before, mtime_calib_after)

    def test_19_to_20_synthetic_artifacts_untouched(self):
        synth_model_path = os.path.join(self.synthetic_artifacts_dir, "v1.0.0", "model.joblib")
        if os.path.exists(synth_model_path):
            mtime_before = os.path.getmtime(synth_model_path)
            self.service.predict(self.sample_payload)
            mtime_after = os.path.getmtime(synth_model_path)
            self.assertEqual(mtime_before, mtime_after)

    def test_21_repeated_inference_is_deterministic(self):
        res1 = self.service.predict(self.sample_payload)
        res2 = self.service.predict(self.sample_payload)

        self.assertEqual(res1["raw_probability"], res2["raw_probability"])
        self.assertEqual(res1["calibrated_probability"], res2["calibrated_probability"])
        self.assertEqual(res1["decision"], res2["decision"])

    def test_22_missing_features_rejected(self):
        invalid_payload = self.sample_payload.copy()
        del invalid_payload["V14"]

        with self.assertRaises(ValueError) as ctx:
            self.service.predict(invalid_payload)
        self.assertIn("Missing required public benchmark feature", str(ctx.exception))

    def test_23_to_26_api_endpoint_predict_success(self):
        req_data = self.sample_payload.copy()
        req_data["include_explanations"] = True

        response = client.post("/api/public/predict", json=req_data)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["dataset_source"], "public")
        self.assertEqual(data["model_version"], "v1.0.0")
        self.assertEqual(data["threshold"], 0.5)
        self.assertIn(data["decision"], ["LEGITIMATE", "FRAUD"])

        # Check explanations present
        self.assertIn("top_positive_features", data)
        self.assertIn("top_negative_features", data)
        self.assertTrue(len(data["top_positive_features"]) > 0)

if __name__ == "__main__":
    unittest.main()
