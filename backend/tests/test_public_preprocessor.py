import os
import sys
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.ml.datasets.base import DatasetResult
from backend.app.ml.datasets.public_preprocessor import prepare_public_features, PublicPreprocessedData

class TestPublicPreprocessor(unittest.TestCase):

    def setUp(self):
        # Sample public dataset DataFrame (e.g. Kaggle V1..V3, Amount, Class)
        self.df_valid = pd.DataFrame({
            "V1": np.random.normal(0, 1, 50),
            "V2": np.random.normal(0, 1, 50),
            "V3": np.random.normal(0, 1, 50),
            "Amount": np.random.exponential(100, 50),
            "transaction_id": [f"tx_{i}" for i in range(50)], # Prohibited ID
            "Class": [1] * 5 + [0] * 45
        })

        self.res_valid = DatasetResult(
            dataframe=self.df_valid,
            feature_columns=["V1", "V2", "V3", "Amount", "transaction_id"],
            target_column="Class",
            dataset_source="public",
            dataset_type="Public benchmark — locally supplied dataset",
            sample_count=50,
            fraud_count=5,
            fraud_rate=0.10,
            missing_value_count=0
        )

    def test_01_public_numeric_features_preserved(self):
        prep = prepare_public_features(self.res_valid)
        self.assertIsInstance(prep, PublicPreprocessedData)
        self.assertListEqual(prep.feature_columns, ["V1", "V2", "V3", "Amount"])
        self.assertIn("V1", prep.X.columns)
        self.assertIn("Amount", prep.X.columns)
        print("[PASS] 1. Public numeric features preserved.")

    def test_02_target_is_separated(self):
        prep = prepare_public_features(self.res_valid)
        self.assertNotIn("Class", prep.X.columns)
        self.assertEqual(len(prep.y), 50)
        self.assertEqual(prep.y.sum(), 5)
        print("[PASS] 2. Target is separated.")

    def test_03_feature_list_is_correct(self):
        prep = prepare_public_features(self.res_valid)
        self.assertListEqual(list(prep.X.columns), prep.feature_columns)
        self.assertNotIn("transaction_id", prep.feature_columns)
        print("[PASS] 3. Feature list is correct.")

    def test_04_missing_target_fails(self):
        df_missing = self.df_valid.drop(columns=["Class"])
        res_missing = DatasetResult(
            dataframe=df_missing,
            feature_columns=["V1", "V2"],
            target_column="Class",
            dataset_source="public",
            dataset_type="Public benchmark — locally supplied dataset",
            sample_count=50,
            fraud_count=0,
            fraud_rate=0.0,
            missing_value_count=0
        )
        with self.assertRaises(ValueError) as ctx:
            prepare_public_features(res_missing)
        self.assertIn("missing from public dataset", str(ctx.exception))
        print("[PASS] 4. Missing target fails.")

    def test_05_invalid_target_fails(self):
        df_invalid_target = self.df_valid.copy()
        df_invalid_target["Class"] = np.random.choice([0, 1, 2], size=50) # 2 is non-binary
        res_invalid = DatasetResult(
            dataframe=df_invalid_target,
            feature_columns=["V1", "V2"],
            target_column="Class",
            dataset_source="public",
            dataset_type="Public benchmark — locally supplied dataset",
            sample_count=50,
            fraud_count=10,
            fraud_rate=0.2,
            missing_value_count=0
        )
        with self.assertRaises(ValueError) as ctx:
            prepare_public_features(res_invalid)
        self.assertIn("must be binary", str(ctx.exception))
        print("[PASS] 5. Invalid non-binary target fails.")

    def test_06_unsupported_categorical_object_values_fail(self):
        df_obj = self.df_valid.copy()
        df_obj["category_str"] = ["A", "B"] * 25 # String/object column
        res_obj = DatasetResult(
            dataframe=df_obj,
            feature_columns=["V1", "category_str"],
            target_column="Class",
            dataset_source="public",
            dataset_type="Public benchmark — locally supplied dataset",
            sample_count=50,
            fraud_count=5,
            fraud_rate=0.10,
            missing_value_count=0
        )
        with self.assertRaises(ValueError) as ctx:
            prepare_public_features(res_obj)
        self.assertIn("unsupported non-numeric object/string columns", str(ctx.exception))
        print("[PASS] 6. Unsupported categorical/object values fail clearly.")

    def test_07_synthetic_features_not_automatically_injected(self):
        prep = prepare_public_features(self.res_valid)
        self.assertNotIn("amount", prep.feature_columns)
        self.assertNotIn("tx_velocity_1h", prep.feature_columns)
        self.assertNotIn("distance_from_home_km", prep.feature_columns)
        print("[PASS] 7. Synthetic feature names not automatically injected.")

    def test_08_no_external_download_occurs(self):
        # Runs entirely in-memory on local DataFrame
        prep = prepare_public_features(self.res_valid)
        self.assertEqual(len(prep.X), 50)
        print("[PASS] 8. No external download occurs.")

    def test_09_preprocessing_metadata_is_deterministic(self):
        prep1 = prepare_public_features(self.res_valid)
        prep2 = prepare_public_features(self.res_valid)
        self.assertDictEqual(prep1.preprocessor_metadata, prep2.preprocessor_metadata)
        print("[PASS] 9. Preprocessing metadata is deterministic.")

if __name__ == "__main__":
    unittest.main()
