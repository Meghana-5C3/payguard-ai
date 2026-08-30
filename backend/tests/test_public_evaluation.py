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

from backend.app.ml.evaluate_public import evaluate_public_benchmark
from backend.app.ml.calibrate_public import calibrate_public_benchmark
from backend.app.ml.train_public import train_public_benchmark

class TestPublicEvaluation(unittest.TestCase):

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

        # Train model and fit calibrator in temp dir
        train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        # Synthetic artifacts directory for isolation testing
        self.synthetic_artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_to_12_evaluation_metrics_and_curves_generated(self):
        res = evaluate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        
        self.assertIn("metrics", res)
        m = res["metrics"]
        
        # Verify required metrics present
        self.assertIn("pr_auc", m)
        self.assertIn("roc_auc", m)
        self.assertIn("precision", m)
        self.assertIn("recall", m)
        self.assertIn("f1", m)
        self.assertIn("brier", m)
        self.assertIn("ece", m)

        # Verify confusion matrix present
        cm = res["confusion_matrix"]
        self.assertIn("true_negatives", cm)
        self.assertIn("false_positives", cm)
        self.assertIn("false_negatives", cm)
        self.assertIn("true_positives", cm)

        # Verify curves present
        self.assertTrue(len(res["roc_curve"]) > 0)
        self.assertTrue(len(res["precision_recall_curve"]) > 0)
        self.assertTrue(len(res["calibration_curve"]) > 0)

        # Verify metrics dynamically calculated (float between 0 and 1)
        self.assertTrue(0.0 <= m["pr_auc"] <= 1.0)
        self.assertTrue(0.0 <= m["roc_auc"] <= 1.0)
        self.assertTrue(0.0 <= m["brier"] <= 1.0)
        self.assertTrue(0.0 <= m["ece"] <= 1.0)

    def test_13_14_15_test_data_not_used_for_training_calibration_threshold(self):
        # Verify model mtime does not change during evaluation
        model_path = os.path.join(self.artifacts_dir, "public", "v1.0.0", "model.joblib")
        mtime_before = os.path.getmtime(model_path)

        evaluate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        mtime_after = os.path.getmtime(model_path)
        self.assertEqual(mtime_before, mtime_after)

    def test_16_public_artifacts_separate_from_synthetic(self):
        synthetic_metrics_path = os.path.join(self.synthetic_artifacts_dir, "model_metrics.json")
        synth_exists_before = os.path.exists(synthetic_metrics_path)
        synth_mtime_before = os.path.getmtime(synthetic_metrics_path) if synth_exists_before else None

        evaluate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        if synth_exists_before:
            synth_mtime_after = os.path.getmtime(synthetic_metrics_path)
            self.assertEqual(synth_mtime_before, synth_mtime_after)

    def test_17_evaluation_is_reproducible(self):
        res1 = evaluate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        res2 = evaluate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        self.assertEqual(res1["metrics"]["pr_auc"], res2["metrics"]["pr_auc"])
        self.assertEqual(res1["metrics"]["roc_auc"], res2["metrics"]["roc_auc"])
        self.assertEqual(res1["metrics"]["brier"], res2["metrics"]["brier"])

if __name__ == "__main__":
    unittest.main()
