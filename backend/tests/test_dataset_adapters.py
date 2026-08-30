import os
import shutil
import tempfile
import unittest
import pandas as pd
import numpy as np

from backend.app.ml.datasets.synthetic import SyntheticDatasetAdapter
from backend.app.ml.datasets.public import PublicDatasetAdapter
from backend.app.ml.datasets.registry import get_dataset_adapter

class TestDatasetAdapters(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_csv = os.path.join(self.temp_dir, "test_public_fraud.csv")

        # Create dummy public CSV
        df = pd.DataFrame({
            "V1": np.random.normal(0, 1, 100),
            "V2": np.random.normal(0, 1, 100),
            "Amount": np.random.exponential(50, 100),
            "transaction_id": [f"tx_{i}" for i in range(100)], # Prohibited ID
            "Class": np.random.choice([0, 1], size=100, p=[0.9, 0.1]) # Target
        })
        df.to_csv(self.sample_csv, index=False)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_synthetic_adapter(self):
        adapter = SyntheticDatasetAdapter(n_samples=500, seed=42)
        pkg = adapter.load_dataset()

        self.assertEqual(pkg.dataset_source, "synthetic")
        self.assertEqual(pkg.n_samples, 500)
        self.assertIn("is_fraud", pkg.df.columns)
        self.assertNotIn("transaction_id", pkg.feature_names)
        self.assertNotIn("user_id", pkg.feature_names)
        print("[PASS] 1. SyntheticDatasetAdapter verified.")

    def test_02_public_adapter(self):
        adapter = PublicDatasetAdapter(csv_path=self.sample_csv)
        pkg = adapter.load_dataset()

        self.assertEqual(pkg.dataset_source, "public")
        self.assertEqual(pkg.n_samples, 100)
        self.assertEqual(pkg.target_name, "Class")
        self.assertNotIn("transaction_id", pkg.feature_names) # Prohibited ID removed
        self.assertIn("V1", pkg.feature_names)
        self.assertIn("V2", pkg.feature_names)
        self.assertIn("Amount", pkg.feature_names)
        print("[PASS] 2. PublicDatasetAdapter verified.")

    def test_03_registry_fallback_behavior(self):
        missing_csv = os.path.join(self.temp_dir, "non_existent.csv")

        # Fallback enabled (default)
        adapter_fb = get_dataset_adapter(source="public", csv_path=missing_csv, fallback_to_synthetic=True)
        pkg_fb = adapter_fb.load_dataset()
        self.assertEqual(pkg_fb.dataset_source, "synthetic") # Gracefully fell back

        # Fallback disabled -> raises FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            get_dataset_adapter(source="public", csv_path=missing_csv, fallback_to_synthetic=False)

        print("[PASS] 3. Registry public missing file fallback behavior verified.")

if __name__ == "__main__":
    unittest.main()
