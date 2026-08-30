import unittest
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from backend.app.ml.leakage_checks import DataLeakageChecker, leakage_checker

class TestDataLeakageChecker(unittest.TestCase):

    def setUp(self):
        self.checker = DataLeakageChecker(max_correlation_threshold=0.95)
        # Deterministic dummy dataset
        np.random.seed(42)
        self.df = pd.DataFrame({
            "f1": np.random.normal(0, 1, 100),
            "f2": np.random.normal(0, 1, 100),
            "is_fraud": np.random.choice([0, 1], size=100, p=[0.9, 0.1])
        })
        self.feature_names = ["f1", "f2"]

    def test_01_target_in_features(self):
        bad_features = ["f1", "f2", "is_fraud"]
        report = self.checker.run_all_checks(self.df, bad_features, target_name="is_fraud")
        self.assertFalse(report["passed"])
        self.assertTrue(any("is_fraud" in err for err in report["errors"]))
        print("[PASS] 1. Target column in features check verified.")

    def test_02_duplicate_column_names(self):
        bad_features = ["f1", "f2", "f1"]
        report = self.checker.run_all_checks(self.df, bad_features, target_name="is_fraud")
        self.assertFalse(report["passed"])
        self.assertTrue(any("Duplicate" in err for err in report["errors"]))
        print("[PASS] 2. Duplicate column names check verified.")

    def test_03_id_columns_detected(self):
        bad_df = self.df.copy()
        bad_df["user_id"] = [f"usr_{i}" for i in range(100)]
        bad_features = ["f1", "f2", "user_id"]
        report = self.checker.run_all_checks(bad_df, bad_features, target_name="is_fraud")
        self.assertFalse(report["passed"])
        self.assertTrue(any("user_id" in err for err in report["errors"]))
        print("[PASS] 3. ID column detection check verified.")

    def test_04_split_index_overlap(self):
        X_train = self.df[["f1", "f2"]].iloc[:60]
        X_test = self.df[["f1", "f2"]].iloc[50:100] # Overlap on indices 50-59
        report = self.checker.run_all_checks(
            df=self.df,
            feature_names=self.feature_names,
            target_name="is_fraud",
            X_train=X_train,
            X_test=X_test
        )
        self.assertFalse(report["passed"])
        self.assertTrue(any("Index overlap" in err for err in report["errors"]))
        print("[PASS] 4. Split index overlap check verified.")

    def test_05_future_features_detected(self):
        bad_df = self.df.copy()
        bad_df["post_tx_refund_amount"] = bad_df["f1"] * 2.0
        bad_features = ["f1", "f2", "post_tx_refund_amount"]
        report = self.checker.run_all_checks(bad_df, bad_features, target_name="is_fraud")
        self.assertFalse(report["passed"])
        self.assertTrue(any("post_tx_refund_amount" in err for err in report["errors"]))
        print("[PASS] 5. Future information feature detection check verified.")

    def test_06_high_target_correlation_detected(self):
        bad_df = self.df.copy()
        # Create feature 99% correlated with target
        bad_df["leaked_target_copy"] = bad_df["is_fraud"] * 1.0 + np.random.normal(0, 0.01, 100)
        bad_features = ["f1", "f2", "leaked_target_copy"]
        report = self.checker.run_all_checks(bad_df, bad_features, target_name="is_fraud")
        self.assertFalse(report["passed"])
        self.assertTrue(any("leaked_target_copy" in err for err in report["errors"]))
        print("[PASS] 6. High target correlation check verified.")

    def test_07_preprocessor_isolation_fails(self):
        X_train = self.df[["f1", "f2"]].iloc[:70]
        X_test = self.df[["f1", "f2"]].iloc[70:]

        scaler = StandardScaler()
        scaler.fit(self.df[["f1", "f2"]]) # FITTED ON FULL DATASET (LEAKAGE)

        report = self.checker.run_all_checks(
            df=self.df,
            feature_names=self.feature_names,
            target_name="is_fraud",
            X_train=X_train,
            X_test=X_test,
            preprocessor=scaler
        )
        self.assertFalse(report["passed"])
        self.assertTrue(any("Preprocessor" in err for err in report["errors"]))
        print("[PASS] 7. Preprocessor state isolation check verified.")

    def test_08_clean_dataset_passes(self):
        X_train = self.df[["f1", "f2"]].iloc[:70]
        X_test = self.df[["f1", "f2"]].iloc[70:]

        scaler = StandardScaler()
        scaler.fit(X_train) # Properly fitted on train set only

        report = self.checker.run_all_checks(
            df=self.df,
            feature_names=self.feature_names,
            target_name="is_fraud",
            X_train=X_train,
            X_test=X_test,
            preprocessor=scaler
        )
        self.assertTrue(report["passed"])
        self.assertEqual(len(report["errors"]), 0)
        print("[PASS] 8. Clean dataset validation check passed.")

if __name__ == "__main__":
    unittest.main()
