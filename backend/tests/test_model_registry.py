import os
import shutil
import tempfile
import unittest
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.isotonic import IsotonicRegression
import xgboost as xgb
import shap

from backend.app.ml.model_registry import ModelRegistry, REQUIRED_METADATA_KEYS
from backend.app.ml.synthetic_data import FEATURE_NAMES

class TestModelRegistry(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.registry = ModelRegistry(self.temp_dir)

        # Create dummy artifacts
        X = pd.DataFrame(np.random.normal(0, 1, (50, len(FEATURE_NAMES))), columns=FEATURE_NAMES)
        y = np.random.choice([0, 1], size=50)

        self.model = xgb.XGBClassifier(n_estimators=5, max_depth=2, random_state=42)
        self.model.fit(X, y)

        val_probs = self.model.predict_proba(X)[:, 1]
        self.calibrator = IsotonicRegression(out_of_bounds="clip")
        self.calibrator.fit(val_probs, y)

        self.explainer = shap.TreeExplainer(self.model)
        self.background_sample = X.sample(n=10, random_state=42)
        self.preprocessor = StandardScaler()
        self.preprocessor.fit(X)

        self.valid_metadata = {
            "model_version": "v1.0.0",
            "feature_version": "v1.0",
            "dataset_source": "Synthetic benchmark — generated dataset",
            "dataset_type": "Synthetic benchmark — generated dataset",
            "dataset_version": "v1.0",
            "training_timestamp": "2026-08-26T17:00:00Z",
            "random_seed": 42,
            "feature_names": FEATURE_NAMES,
            "training_sample_count": 35,
            "validation_sample_count": 8,
            "test_sample_count": 7
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_model_save(self):
        version_dir = self.registry.save_model_package(
            model=self.model,
            calibrator=self.calibrator,
            shap_explainer=self.explainer,
            background_sample=self.background_sample,
            metadata=self.valid_metadata,
            preprocessor=self.preprocessor,
            version="v1.0.0"
        )
        self.assertTrue(os.path.exists(version_dir))
        self.assertTrue(os.path.exists(os.path.join(version_dir, "model.joblib")))
        self.assertTrue(os.path.exists(os.path.join(version_dir, "calibrator.joblib")))
        self.assertTrue(os.path.exists(os.path.join(version_dir, "shap_explainer.joblib")))
        self.assertTrue(os.path.exists(os.path.join(version_dir, "background_sample.joblib")))
        self.assertTrue(os.path.exists(os.path.join(version_dir, "preprocessor.joblib")))
        self.assertTrue(os.path.exists(os.path.join(version_dir, "metadata.json")))
        print("[PASS] 1. ModelRegistry save_model_package verified.")

    def test_02_model_load(self):
        self.registry.save_model_package(
            model=self.model,
            calibrator=self.calibrator,
            shap_explainer=self.explainer,
            background_sample=self.background_sample,
            metadata=self.valid_metadata,
            preprocessor=self.preprocessor,
            version="v1.0.0"
        )

        package = self.registry.load_model_package(version="v1.0.0")
        self.assertIsNotNone(package["model"])
        self.assertIsNotNone(package["calibrator"])
        self.assertIsNotNone(package["shap_explainer"])
        self.assertIsNotNone(package["background_sample"])
        self.assertIsNotNone(package["preprocessor"])
        self.assertEqual(package["metadata"]["model_version"], "v1.0.0")
        print("[PASS] 2. ModelRegistry load_model_package verified.")

    def test_03_metadata_validation(self):
        invalid_metadata = self.valid_metadata.copy()
        del invalid_metadata["random_seed"] # Missing key

        with self.assertRaises(ValueError):
            self.registry.validate_metadata(invalid_metadata)

        invalid_metadata_none = self.valid_metadata.copy()
        invalid_metadata_none["model_version"] = None

        with self.assertRaises(ValueError):
            self.registry.validate_metadata(invalid_metadata_none)

        print("[PASS] 3. ModelRegistry metadata validation verified.")

    def test_04_feature_compatibility(self):
        expected_features = FEATURE_NAMES
        input_features_correct = list(FEATURE_NAMES)
        self.assertTrue(ModelRegistry.check_feature_compatibility(input_features_correct, expected_features))

        input_features_bad = list(FEATURE_NAMES)[:-1] # Missing last feature
        with self.assertRaises(ValueError):
            ModelRegistry.check_feature_compatibility(input_features_bad, expected_features)

        print("[PASS] 4. ModelRegistry feature compatibility check verified.")

if __name__ == "__main__":
    unittest.main()
