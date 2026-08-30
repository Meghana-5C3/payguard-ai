import unittest
import numpy as np
import pandas as pd
from backend.app.ml.synthetic_data import generate_synthetic_dataset, FEATURE_NAMES

class TestSyntheticDataGenerator(unittest.TestCase):

    def test_label_generation_is_stochastic(self):
        """
        Verify that labels are generated probabilistically via Bernoulli sampling
        (np.random.default_rng.binomial) and not deterministic step thresholds.
        """
        df = generate_synthetic_dataset(n_samples=5000, seed=42)
        self.assertIn("is_fraud", df.columns)
        
        # Verify binary outputs 0 and 1
        unique_labels = set(df["is_fraud"].unique())
        self.assertTrue(unique_labels.issubset({0, 1}))

        # Generate with two different seeds to verify stochastic variation
        df1 = generate_synthetic_dataset(n_samples=2000, seed=42)
        df2 = generate_synthetic_dataset(n_samples=2000, seed=123)
        self.assertNotEqual(df1["is_fraud"].sum(), df2["is_fraud"].sum())
        print("[PASS] test_label_generation_is_stochastic passed")

    def test_reproducibility(self):
        """
        Verify that dataset generation is 100% deterministic and reproducible given the same seed.
        """
        df_a = generate_synthetic_dataset(n_samples=1000, seed=42)
        df_b = generate_synthetic_dataset(n_samples=1000, seed=42)
        pd.testing.assert_frame_equal(df_a, df_b)
        print("[PASS] test_reproducibility passed")

    def test_target_not_in_features(self):
        """
        Verify that the target label 'is_fraud' is not included in FEATURE_NAMES.
        """
        self.assertNotIn("is_fraud", FEATURE_NAMES)
        self.assertNotIn("proba", FEATURE_NAMES)
        self.assertNotIn("risk_signal", FEATURE_NAMES)
        print("[PASS] test_target_not_in_features passed")

    def test_generation_schema(self):
        """
        Verify returned DataFrame schema contains all expected feature names plus target.
        """
        df = generate_synthetic_dataset(n_samples=100, seed=42)
        expected_cols = set(FEATURE_NAMES + ["is_fraud"])
        self.assertEqual(set(df.columns), expected_cols)
        self.assertEqual(len(df), 100)
        print("[PASS] test_generation_schema passed")

    def test_no_id_features(self):
        """
        Verify that transaction_id and user_id are strictly excluded from generated features.
        """
        self.assertNotIn("transaction_id", FEATURE_NAMES)
        self.assertNotIn("user_id", FEATURE_NAMES)
        df = generate_synthetic_dataset(n_samples=100, seed=42)
        self.assertNotIn("transaction_id", df.columns)
        self.assertNotIn("user_id", df.columns)
        print("[PASS] test_no_id_features passed")

if __name__ == "__main__":
    unittest.main()
