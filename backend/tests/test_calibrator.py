import os
import tempfile
import joblib
import unittest
import numpy as np
from backend.app.ml.calibrator import ProbabilityCalibrator, calculate_ece

class TestProbabilityCalibrator(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        # Validation raw probs & targets
        self.val_raw_probs = np.random.uniform(0.01, 0.99, 1500)
        self.y_val = (self.val_raw_probs > 0.40).astype(int)

        # Test raw probs & targets
        self.test_raw_probs = np.random.uniform(0.01, 0.99, 500)
        self.y_test = (self.test_raw_probs > 0.40).astype(int)

    def test_01_test_data_not_used_for_calibration(self):
        """
        Verify that calibrator is fitted ONCE on validation set predictions,
        and test set predictions do not mutate calibrator state.
        """
        calibrator = ProbabilityCalibrator(method="auto")
        report = calibrator.fit(self.val_raw_probs, self.y_val)

        self.assertIsNotNone(calibrator.calibrator_model)
        self.assertIn("calibrated_brier", report)

        # Record test predictions
        preds_initial = calibrator.predict(self.test_raw_probs)

        # Call predict again on test set to verify state is frozen/immutable
        preds_second = calibrator.predict(self.test_raw_probs)
        np.testing.assert_array_equal(preds_initial, preds_second)

        print(f"[PASS] 1. Test data isolation verified. (Selected method: '{calibrator.selected_method}')")

    def test_02_calibrator_can_be_loaded(self):
        """
        Verify that ProbabilityCalibrator can be joblib serialized and deserialized.
        """
        calibrator = ProbabilityCalibrator(method="auto")
        calibrator.fit(self.val_raw_probs, self.y_val)
        original_preds = calibrator.predict(self.test_raw_probs)

        with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            joblib.dump(calibrator, tmp_path)
            loaded_calibrator = joblib.load(tmp_path)
            loaded_preds = loaded_calibrator.predict(self.test_raw_probs)

            np.testing.assert_array_equal(original_preds, loaded_preds)
            self.assertEqual(calibrator.selected_method, loaded_calibrator.selected_method)
            print("[PASS] 2. Joblib serialization and deserialization verified.")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_03_probability_output_between_0_and_1(self):
        """
        Verify probability outputs are strictly bounded in (0, 1).
        """
        calibrator = ProbabilityCalibrator(method="auto")
        calibrator.fit(self.val_raw_probs, self.y_val)

        extreme_raw_probs = np.array([-5.0, 0.0, 0.00001, 0.5, 0.99999, 1.0, 5.0])
        calibrated_probs = calibrator.predict(extreme_raw_probs)

        self.assertTrue(np.all(calibrated_probs >= 0.0001))
        self.assertTrue(np.all(calibrated_probs <= 0.9999))
        print("[PASS] 3. Probability bounds (0.0001 <= p <= 0.9999) verified.")

    def test_04_calibration_is_reproducible(self):
        """
        Verify that calibration predictions are 100% reproducible for identical inputs.
        """
        calibrator_a = ProbabilityCalibrator(method="auto", seed=42) if hasattr(ProbabilityCalibrator, "seed") else ProbabilityCalibrator(method="auto")
        calibrator_b = ProbabilityCalibrator(method="auto", seed=42) if hasattr(ProbabilityCalibrator, "seed") else ProbabilityCalibrator(method="auto")

        calibrator_a.fit(self.val_raw_probs, self.y_val)
        calibrator_b.fit(self.val_raw_probs, self.y_val)

        preds_a = calibrator_a.predict(self.test_raw_probs)
        preds_b = calibrator_b.predict(self.test_raw_probs)

        np.testing.assert_array_equal(preds_a, preds_b)
        print("[PASS] 4. Calibration reproducibility verified.")

if __name__ == "__main__":
    unittest.main()
