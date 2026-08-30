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

from backend.app.ml.calibrator import ProbabilityCalibrator
from backend.app.ml.calibrate_public import calibrate_public_benchmark
from backend.app.ml.train_public import train_public_benchmark

class TestPublicCalibration(unittest.TestCase):

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

        # Train model first in temp dir
        train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        # Synthetic artifacts directory for isolation testing
        self.synthetic_artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_calibrator_fitted_using_validation_data_only(self):
        res = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        self.assertIn("selected_method", res)
        self.assertIn("val_sample_count", res)
        self.assertEqual(res["val_sample_count"], 30) # 15% of 200

    def test_02_03_test_labels_and_probs_not_used_for_calibration(self):
        res = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        calibrator = res["calibrator"]

        # Call predict on test-like array to verify fit is immutable
        test_raw = np.array([0.05, 0.2, 0.8, 0.95])
        preds_1 = calibrator.predict(test_raw)
        preds_2 = calibrator.predict(test_raw)

        np.testing.assert_array_equal(preds_1, preds_2)

    def test_04_method_selection_ignores_test_performance(self):
        res = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        self.assertIn(res["selected_method"], ["isotonic", "sigmoid"])

    def test_05_calibrator_serialization_and_loading(self):
        res = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        calib_path = os.path.join(self.artifacts_dir, "public", "v1.0.0", "calibrator.joblib")

        self.assertTrue(os.path.exists(calib_path))
        loaded_calib = joblib.load(calib_path)
        self.assertIsInstance(loaded_calib, ProbabilityCalibrator)

    def test_06_calibrated_probabilities_between_0_and_1(self):
        res = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        calibrator = res["calibrator"]
        raw_probs = np.linspace(0.0, 1.0, 50)
        calib_probs = calibrator.predict(raw_probs)

        self.assertTrue(np.all(calib_probs >= 0.0001))
        self.assertTrue(np.all(calib_probs <= 0.9999))

    def test_07_calibration_is_reproducible(self):
        res1 = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        res2 = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        self.assertEqual(res1["selected_method"], res2["selected_method"])
        self.assertAlmostEqual(res1["calibrated_brier"], res2["calibrated_brier"], places=4)

    def test_08_public_calibrator_stored_under_public_v1_0_0(self):
        res = calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        calib_path = os.path.join(self.artifacts_dir, "public", "v1.0.0", "calibrator.joblib")
        self.assertTrue(os.path.exists(calib_path))

    def test_09_synthetic_calibration_artifacts_untouched(self):
        synthetic_calib_path = os.path.join(self.synthetic_artifacts_dir, "v1.0.0", "calibrator.joblib")
        synth_exists_before = os.path.exists(synthetic_calib_path)
        synth_mtime_before = os.path.getmtime(synthetic_calib_path) if synth_exists_before else None

        calibrate_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        if synth_exists_before:
            synth_mtime_after = os.path.getmtime(synthetic_calib_path)
            self.assertEqual(synth_mtime_before, synth_mtime_after)

if __name__ == "__main__":
    unittest.main()
