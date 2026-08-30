import os
import sys
import json
import shutil
import tempfile
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.ml.datasets.registry import get_dataset
from backend.app.ml.train_public import train_public_benchmark

class TestPublicTraining(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_csv = os.path.join(self.temp_dir, "creditcard_sample.csv")
        self.artifacts_dir = os.path.join(self.temp_dir, "artifacts")

        # Create dummy public credit card dataset (100 rows)
        df = pd.DataFrame({
            "Time": np.arange(100),
            "V1": np.random.normal(0, 1, 100),
            "V2": np.random.normal(0, 1, 100),
            "V3": np.random.normal(0, 1, 100),
            "Amount": np.random.exponential(50, 100),
            "Class": [1] * 10 + [0] * 90
        })
        df.to_csv(self.sample_csv, index=False)

        # Synthetic artifacts directory for isolation testing
        self.synthetic_artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_public_dataset_loads_through_registry(self):
        ds = get_dataset(source="public", csv_path=self.sample_csv, target_column="Class")
        self.assertEqual(ds.dataset_source, "public")
        self.assertEqual(ds.sample_count, 100)

    def test_02_target_is_class(self):
        ds = get_dataset(source="public", csv_path=self.sample_csv, target_column="Class")
        self.assertEqual(ds.target_column, "Class")

    def test_03_public_features_remain_native(self):
        ds = get_dataset(source="public", csv_path=self.sample_csv, target_column="Class")
        self.assertIn("V1", ds.feature_columns)
        self.assertIn("Amount", ds.feature_columns)
        self.assertIn("Time", ds.feature_columns)

    def test_04_synthetic_features_not_injected(self):
        ds = get_dataset(source="public", csv_path=self.sample_csv, target_column="Class")
        self.assertNotIn("tx_velocity_1h", ds.feature_columns)
        self.assertNotIn("is_new_device", ds.feature_columns)
        self.assertNotIn("ip_reputation_score", ds.feature_columns)

    def test_05_06_split_sizes_and_reproducibility(self):
        meta1 = train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        self.assertEqual(meta1["train_size"], 70)
        self.assertEqual(meta1["validation_size"], 15)
        self.assertEqual(meta1["test_size"], 15)

    def test_07_08_model_trains_on_train_set_only(self):
        meta = train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        self.assertEqual(meta["train_size"], 70)
        self.assertEqual(meta["dataset_source"], "public")

    def test_09_10_public_artifacts_saved_separately_synthetic_untouched(self):
        synthetic_model_path = os.path.join(self.synthetic_artifacts_dir, "v1.0.0", "model.joblib")
        synth_exists_before = os.path.exists(synthetic_model_path)
        synth_mtime_before = os.path.getmtime(synthetic_model_path) if synth_exists_before else None

        meta = train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)

        public_model_path = os.path.join(self.artifacts_dir, "public", "v1.0.0", "model.joblib")
        self.assertTrue(os.path.exists(public_model_path))

        if synth_exists_before:
            synth_mtime_after = os.path.getmtime(synthetic_model_path)
            self.assertEqual(synth_mtime_before, synth_mtime_after)

    def test_11_metadata_contains_correct_dataset_source_and_type(self):
        meta = train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        self.assertEqual(meta["dataset_source"], "public")
        self.assertEqual(meta["dataset_type"], "Public benchmark — locally supplied dataset")
        self.assertEqual(meta["target_column"], "Class")

    def test_12_training_is_reproducible(self):
        meta1 = train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        meta2 = train_public_benchmark(artifacts_dir=self.artifacts_dir, csv_path=self.sample_csv, version="v1.0.0", seed=42)
        self.assertEqual(meta1["random_seed"], meta2["random_seed"])
        self.assertEqual(meta1["fraud_count"], meta2["fraud_count"])

if __name__ == "__main__":
    unittest.main()
