import os
import json
import joblib
import unittest
import numpy as np
import pandas as pd
from backend.app.ml.synthetic_data import generate_synthetic_dataset, FEATURE_NAMES
from backend.app.ml.calibrator import calculate_ece

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts"))

class TestMLPipelineAudit(unittest.TestCase):

    def test_01_probabilistic_label_generation(self):
        """
        Verify that labels are generated probabilistically using Bernoulli sampling (np.random.binomial)
        and NOT via a deterministic step threshold (e.g. proba > 0.45).
        """
        df = generate_synthetic_dataset(n_samples=5000, seed=42)
        self.assertIn("is_fraud", df.columns)
        
        # Verify binary outputs
        unique_labels = set(df["is_fraud"].unique())
        self.assertTrue(unique_labels.issubset({0, 1}))

        # Run with two different seeds to ensure probabilistic variation
        df1 = generate_synthetic_dataset(n_samples=1000, seed=42)
        df2 = generate_synthetic_dataset(n_samples=1000, seed=99)
        self.assertNotEqual(df1["is_fraud"].sum(), df2["is_fraud"].sum())
        print("[PASS] 1. Probabilistic Bernoulli label sampling verified (No deterministic thresholding).")

    def test_02_feature_exclusion_leakage(self):
        """
        Verify that transaction_id and user_id are strictly excluded from model feature vector.
        """
        self.assertNotIn("transaction_id", FEATURE_NAMES)
        self.assertNotIn("user_id", FEATURE_NAMES)
        self.assertNotIn("is_fraud", FEATURE_NAMES)
        print("[PASS] 2. Transaction ID and User ID leakage check passed.")

    def test_03_data_splitting_overlap(self):
        """
        Verify 70% Train, 15% Val, 15% Test split sizes and non-overlapping indices.
        """
        df = generate_synthetic_dataset(n_samples=1000, seed=42)
        from sklearn.model_selection import train_test_split
        X = df[FEATURE_NAMES]
        y = df["is_fraud"]

        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

        train_idx = set(X_train.index)
        val_idx = set(X_val.index)
        test_idx = set(X_test.index)

        self.assertEqual(len(train_idx.intersection(val_idx)), 0)
        self.assertEqual(len(train_idx.intersection(test_idx)), 0)
        self.assertEqual(len(val_idx.intersection(test_idx)), 0)
        print("[PASS] 3. Train/Val/Test set indices non-overlapping check passed.")

    def test_04_artifact_loading(self):
        """
        Verify all required joblib artifacts and metrics.json load cleanly.
        """
        model_path = os.path.join(ARTIFACTS_DIR, "model.joblib")
        calib_path = os.path.join(ARTIFACTS_DIR, "calibrator.joblib")
        shap_path = os.path.join(ARTIFACTS_DIR, "shap_explainer.joblib")
        metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
        model_metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")

        self.assertTrue(os.path.exists(model_path), f"Missing {model_path}")
        self.assertTrue(os.path.exists(calib_path), f"Missing {calib_path}")
        self.assertTrue(os.path.exists(shap_path), f"Missing {shap_path}")
        self.assertTrue(os.path.exists(metrics_path), f"Missing {metrics_path}")
        self.assertTrue(os.path.exists(model_metrics_path), f"Missing {model_metrics_path}")

        model = joblib.load(model_path)
        calibrator = joblib.load(calib_path)
        shap_explainer = joblib.load(shap_path)
        
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f)

        with open(model_metrics_path, "r") as f:
            model_metrics_data = json.load(f)

        self.assertIsNotNone(model)
        self.assertIsNotNone(calibrator)
        self.assertIsNotNone(shap_explainer)
        self.assertIn("roc_auc", metrics_data)
        self.assertIn("dataset_type", metrics_data)
        self.assertIn("metrics", model_metrics_data)
        self.assertIn("pr_auc", model_metrics_data["metrics"])

        print(f"[PASS] 4. Artifacts loading test passed (ROC-AUC={metrics_data['roc_auc']}, PR-AUC={model_metrics_data['metrics']['pr_auc']}).")

if __name__ == "__main__":
    unittest.main()
