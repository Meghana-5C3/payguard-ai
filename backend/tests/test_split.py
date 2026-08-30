import unittest
import numpy as np
import pandas as pd
from backend.app.ml.split import split_dataset
from backend.app.ml.synthetic_data import FEATURE_NAMES

class TestDatasetSplitter(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        n = 1000
        self.df = pd.DataFrame({
            feat: np.random.normal(0, 1, n) for feat in FEATURE_NAMES
        })
        self.df["timestamp"] = pd.date_range(start="2026-01-01", periods=n, freq="min")
        self.df["is_fraud"] = np.random.choice([0, 1], size=n, p=[0.95, 0.05])

    def test_01_split_ratios_and_counts(self):
        X_tr, X_va, X_te, y_tr, y_va, y_te = split_dataset(
            self.df, FEATURE_NAMES, target_name="is_fraud",
            train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42
        )
        self.assertEqual(len(X_tr), 700)
        self.assertEqual(len(X_va), 150)
        self.assertEqual(len(X_te), 150)
        self.assertEqual(len(y_tr), 700)
        self.assertEqual(len(y_va), 150)
        self.assertEqual(len(y_te), 150)
        print("[PASS] 1. Split ratios (70/15/15) verified.")

    def test_02_no_index_overlap(self):
        X_tr, X_va, X_te, y_tr, y_va, y_te = split_dataset(
            self.df, FEATURE_NAMES, target_name="is_fraud", seed=42
        )
        tr_idx, va_idx, te_idx = set(X_tr.index), set(X_va.index), set(X_te.index)
        self.assertEqual(len(tr_idx & va_idx), 0)
        self.assertEqual(len(tr_idx & te_idx), 0)
        self.assertEqual(len(va_idx & te_idx), 0)
        print("[PASS] 2. No index overlap across splits verified.")

    def test_03_column_consistency(self):
        X_tr, X_va, X_te, y_tr, y_va, y_te = split_dataset(
            self.df, FEATURE_NAMES, target_name="is_fraud", seed=42
        )
        self.assertEqual(list(X_tr.columns), FEATURE_NAMES)
        self.assertEqual(list(X_va.columns), FEATURE_NAMES)
        self.assertEqual(list(X_te.columns), FEATURE_NAMES)
        print("[PASS] 3. Column consistency across splits verified.")

    def test_04_target_separated(self):
        X_tr, X_va, X_te, y_tr, y_va, y_te = split_dataset(
            self.df, FEATURE_NAMES, target_name="is_fraud", seed=42
        )
        self.assertNotIn("is_fraud", X_tr.columns)
        self.assertNotIn("is_fraud", X_va.columns)
        self.assertNotIn("is_fraud", X_te.columns)
        print("[PASS] 4. Target separation verified.")

    def test_05_chronological_splitting(self):
        X_tr, X_va, X_te, y_tr, y_va, y_te = split_dataset(
            self.df, FEATURE_NAMES, target_name="is_fraud",
            timestamp_column="timestamp"
        )
        self.assertEqual(len(X_tr), 700)
        self.assertEqual(len(X_va), 150)
        self.assertEqual(len(X_te), 150)
        print("[PASS] 5. Chronological splitting verified.")

    def test_06_reproducibility(self):
        s1 = split_dataset(self.df, FEATURE_NAMES, target_name="is_fraud", seed=42)
        s2 = split_dataset(self.df, FEATURE_NAMES, target_name="is_fraud", seed=42)
        pd.testing.assert_frame_equal(s1[0], s2[0])
        pd.testing.assert_frame_equal(s1[1], s2[1])
        pd.testing.assert_frame_equal(s1[2], s2[2])
        print("[PASS] 6. Fixed seed reproducibility verified.")

if __name__ == "__main__":
    unittest.main()
