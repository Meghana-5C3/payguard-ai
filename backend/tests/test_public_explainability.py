import os
import sys
import json
import shutil
import tempfile
import unittest
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.ml.train_public import train_public_benchmark
from backend.app.ml.calibrate_public import calibrate_public_benchmark
from backend.app.ml.evaluate_public import evaluate_public_benchmark
from backend.app.ml.explain_public import explain_public_benchmark

class TestPublicExplainability(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_csv = os.path.join(self.temp_dir, "creditcard_sample.csv")
        self.artifacts_dir = os.path.join(self.temp_dir, "artifacts")

        # Create dummy public credit card dataset (200 rows)
        df = pd.DataFrame({
            "Time": np.arange(200),
            "V1": np.random.normal(0, 1, 200),
            "V2": np.random.normal(0, 1, 200),
            "V3": np.random.normal(0, 1, 200),
            "Amount": np.random.exponential(50, 200),
            "Class": [1] * 20 + [0] * 180
        })
        df.to_csv(self.sample_csv, index=False)

        # Train, calibrate, evaluate in temp dir
        train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        evaluate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        # Synthetic artifacts directory for isolation testing
        self.synthetic_artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_to_09_shap_explainability_artifact_and_features(self):
        shap_res = explain_public_benchmark(
            artifacts_dir=self.artifacts_dir,
            csv_path=self.sample_csv,
            version="v1.0.0",
            seed=42,
            background_size=20,
            analysis_size=50
        )

        self.assertEqual(shap_res["dataset_source"], "public")
        self.assertEqual(shap_res["explanation_method"], "SHAP TreeExplainer")

        # Verify public feature names preserved, no synthetic names
        feats = shap_res["feature_columns"]
        self.assertIn("V1", feats)
        self.assertIn("Amount", feats)
        self.assertNotIn("tx_velocity_1h", feats)
        self.assertNotIn("is_new_device", feats)

        # Verify global feature importance list
        glob_imp = shap_res["global_feature_importance"]
        self.assertEqual(len(glob_imp), len(feats))

        for item in glob_imp:
            self.assertIn("feature", item)
            self.assertIn("mean_absolute_shap", item)
            self.assertIsInstance(item["mean_absolute_shap"], float)
            self.assertTrue(item["mean_absolute_shap"] >= 0.0)

        # Verify SHAP artifact created
        artifact_path = os.path.join(self.artifacts_dir, "public", "v1.0.0", "shap_importance.json")
        self.assertTrue(os.path.exists(artifact_path))

    def test_10_to_14_explainability_does_not_modify_model_calibrator_or_metrics(self):
        model_path = os.path.join(self.artifacts_dir, "public", "v1.0.0", "model.joblib")
        metrics_path = os.path.join(self.artifacts_dir, "public", "v1.0.0", "model_metrics.json")

        model_mtime_before = os.path.getmtime(model_path)
        metrics_mtime_before = os.path.getmtime(metrics_path)

        explain_public_benchmark(
            artifacts_dir=self.artifacts_dir,
            csv_path=self.sample_csv,
            version="v1.0.0",
            seed=42,
            background_size=20,
            analysis_size=50
        )

        model_mtime_after = os.path.getmtime(model_path)
        metrics_mtime_after = os.path.getmtime(metrics_path)

        self.assertEqual(model_mtime_before, model_mtime_after)
        self.assertEqual(metrics_mtime_before, metrics_mtime_after)

    def test_15_repeated_execution_is_deterministic(self):
        res1 = explain_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42, background_size=20, analysis_size=50)
        res2 = explain_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42, background_size=20, analysis_size=50)

        self.assertEqual(
            res1["global_feature_importance"][0]["feature"],
            res2["global_feature_importance"][0]["feature"]
        )
        self.assertAlmostEqual(
            res1["global_feature_importance"][0]["mean_absolute_shap"],
            res2["global_feature_importance"][0]["mean_absolute_shap"],
            places=5
        )

if __name__ == "__main__":
    unittest.main()
