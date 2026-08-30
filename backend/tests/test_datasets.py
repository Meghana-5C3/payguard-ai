import os
import sys
import shutil
import tempfile
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.ml.datasets.base import DatasetResult
from backend.app.ml.datasets.synthetic import load_synthetic_dataset
from backend.app.ml.datasets.public import load_public_csv
from backend.app.ml.datasets.registry import get_dataset

class TestDatasetsModule(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.valid_csv = os.path.join(self.temp_dir, "valid_fraud.csv")
        self.non_binary_csv = os.path.join(self.temp_dir, "non_binary_fraud.csv")
        self.missing_target_csv = os.path.join(self.temp_dir, "missing_target_fraud.csv")

        # 1. Valid public CSV (100 rows, 10 fraud)
        df_valid = pd.DataFrame({
            "V1": np.random.normal(0, 1, 100),
            "V2": np.random.normal(0, 1, 100),
            "Amount": np.random.exponential(50, 100),
            "Class": [1] * 10 + [0] * 90
        })
        df_valid.to_csv(self.valid_csv, index=False)

        # 2. Non-binary target CSV
        df_non_binary = pd.DataFrame({
            "V1": [1.0, 2.0, 3.0],
            "Class": [0, 1, 2] # 2 is non-binary
        })
        df_non_binary.to_csv(self.non_binary_csv, index=False)

        # 3. Missing target CSV
        df_missing_target = pd.DataFrame({
            "V1": [1.0, 2.0],
            "OtherCol": [0, 1]
        })
        df_missing_target.to_csv(self.missing_target_csv, index=False)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_synthetic_adapter_works(self):
        result = load_synthetic_dataset(n_samples=500, seed=42)
        self.assertIsInstance(result, DatasetResult)
        self.assertEqual(result.dataset_source, "synthetic")
        self.assertEqual(result.dataset_type, "Synthetic benchmark — generated dataset")
        self.assertEqual(result.sample_count, 500)
        self.assertGreater(result.fraud_count, 0)
        self.assertGreater(result.fraud_rate, 0.0)
        self.assertEqual(result.missing_value_count, 0)
        self.assertEqual(result.target_column, "is_fraud")

    def test_02_synthetic_metadata_correct(self):
        result = load_synthetic_dataset(n_samples=1000, seed=42)
        expected_fraud = int(result.dataframe["is_fraud"].sum())
        expected_rate = float(result.dataframe["is_fraud"].mean())

        self.assertEqual(result.fraud_count, expected_fraud)
        self.assertAlmostEqual(result.fraud_rate, expected_rate, places=4)
        self.assertEqual(len(result.feature_columns), 12)

    def test_03_public_csv_loads_correctly(self):
        result = load_public_csv(path=self.valid_csv, target_column="Class")
        self.assertIsInstance(result, DatasetResult)
        self.assertEqual(result.dataset_source, "public")
        self.assertEqual(result.dataset_type, "Public benchmark — locally supplied dataset")
        self.assertEqual(result.sample_count, 100)
        self.assertEqual(result.fraud_count, 10)
        self.assertAlmostEqual(result.fraud_rate, 0.10, places=4)
        self.assertEqual(result.target_column, "Class")
        self.assertListEqual(result.feature_columns, ["V1", "V2", "Amount"])

    def test_04_missing_target_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            load_public_csv(path=self.missing_target_csv, target_column="Class")
        self.assertIn("Target column 'Class' not found", str(ctx.exception))

    def test_05_non_binary_target_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            load_public_csv(path=self.non_binary_csv, target_column="Class")
        self.assertIn("must be binary", str(ctx.exception))

    def test_06_missing_file_raises_error(self):
        missing_path = os.path.join(self.temp_dir, "non_existent_file.csv")
        with self.assertRaises((FileNotFoundError, ValueError)):
            load_public_csv(path=missing_path, target_column="Class")

        with self.assertRaises(ValueError) as ctx:
            get_dataset(source="public", csv_path=missing_path, target_column="Class")
        self.assertIn("not found", str(ctx.exception))

    def test_07_fraud_statistics_calculated_dynamically(self):
        # Create CSV with 5 fraud out of 20
        custom_csv = os.path.join(self.temp_dir, "custom_stats.csv")
        pd.DataFrame({"x": range(20), "target": [1]*5 + [0]*15}).to_csv(custom_csv, index=False)

        res = load_public_csv(path=custom_csv, target_column="target")
        self.assertEqual(res.sample_count, 20)
        self.assertEqual(res.fraud_count, 5)
        self.assertAlmostEqual(res.fraud_rate, 0.25, places=4)

    def test_08_synthetic_and_public_remain_separate(self):
        syn = get_dataset(source="synthetic", n_samples=200)
        pub = get_dataset(source="public", csv_path=self.valid_csv, target_column="Class")

        self.assertNotEqual(syn.dataset_source, pub.dataset_source)
        self.assertNotEqual(syn.dataset_type, pub.dataset_type)
        self.assertNotEqual(syn.target_column, pub.target_column)
        self.assertNotEqual(syn.feature_columns, pub.feature_columns)

if __name__ == "__main__":
    unittest.main()
