import os
import json
import tempfile
import unittest
import numpy as np
from backend.app.ml.evaluator import ModelEvaluator

class TestModelEvaluator(unittest.TestCase):

    def setUp(self):
        # Known small array: Perfect rank order
        self.y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
        self.y_prob = np.array([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])

    def test_01_perfect_predictions_metrics(self):
        report = ModelEvaluator.evaluate_performance(self.y_true, self.y_prob, threshold=0.5)
        metrics = report["metrics"]

        self.assertEqual(metrics["roc_auc"], 1.0)
        self.assertEqual(metrics["pr_auc"], 1.0)
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["f1"], 1.0)

        # Expected Brier score calculation: np.mean((y_prob - y_true)**2)
        expected_brier = round(float(np.mean((self.y_prob - self.y_true) ** 2)), 4)
        self.assertEqual(metrics["brier"], expected_brier)
        self.assertIn("ece", metrics)
        print(f"[PASS] 1. Evaluator metrics on known small array verified (Brier={metrics['brier']}, ECE={metrics['ece']}).")

    def test_02_imbalanced_pr_auc_importance(self):
        # Imbalanced array: 1 positive out of 10 samples
        y_true_imb = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        y_prob_imb = np.array([0.05, 0.05, 0.1, 0.1, 0.2, 0.2, 0.3, 0.4, 0.5, 0.9])

        report = ModelEvaluator.evaluate_performance(y_true_imb, y_prob_imb, threshold=0.5)
        metrics = report["metrics"]

        self.assertIn("pr_auc", metrics)
        self.assertEqual(metrics["roc_auc"], 1.0)
        self.assertEqual(metrics["pr_auc"], 1.0)
        print(f"[PASS] 2. Imbalanced PR-AUC evaluation verified (PR-AUC={metrics['pr_auc']}).")

    def test_03_save_metrics(self):
        report = ModelEvaluator.evaluate_performance(self.y_true, self.y_prob)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            ModelEvaluator.save_metrics(report, tmp_path)
            self.assertTrue(os.path.exists(tmp_path))

            with open(tmp_path, "r") as f:
                loaded = json.load(f)

            self.assertEqual(loaded["metrics"]["roc_auc"], 1.0)
            self.assertEqual(loaded["metrics"]["pr_auc"], 1.0)
            self.assertIn("confusion_matrix", loaded)
            self.assertIn("calibration_curve", loaded)
            print("[PASS] 3. save_metrics to model_metrics.json verified.")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()
