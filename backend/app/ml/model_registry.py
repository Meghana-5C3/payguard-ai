import os
import json
import joblib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

REQUIRED_METADATA_KEYS = [
    "model_version",
    "feature_version",
    "dataset_source",
    "dataset_type",
    "dataset_version",
    "training_timestamp",
    "random_seed",
    "feature_names",
    "training_sample_count",
    "validation_sample_count",
    "test_sample_count"
]

class ModelRegistry:
    """
    Model Registry for saving, loading, versioning, and validating ML model artifacts and metadata.
    """

    def __init__(self, registry_dir: str):
        self.registry_dir = os.path.abspath(registry_dir)
        os.makedirs(self.registry_dir, exist_ok=True)

    def save_model_package(
        self,
        model: Any,
        calibrator: Any,
        shap_explainer: Any,
        background_sample: Any,
        metadata: Dict[str, Any],
        preprocessor: Optional[Any] = None,
        version: str = "v1.0.0"
    ) -> str:
        """
        Saves versioned model artifacts and validates required metadata.
        """
        # Validate metadata fields
        self.validate_metadata(metadata)

        version_dir = os.path.join(self.registry_dir, version)
        os.makedirs(version_dir, exist_ok=True)

        # Save joblib artifacts
        joblib.dump(model, os.path.join(version_dir, "model.joblib"))
        joblib.dump(calibrator, os.path.join(version_dir, "calibrator.joblib"))
        joblib.dump(shap_explainer, os.path.join(version_dir, "shap_explainer.joblib"))
        joblib.dump(background_sample, os.path.join(version_dir, "background_sample.joblib"))

        if preprocessor is not None:
            joblib.dump(preprocessor, os.path.join(version_dir, "preprocessor.joblib"))

        # Save metadata.json
        with open(os.path.join(version_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        # Also update current/latest pointer artifacts directory
        for fname in ["model.joblib", "calibrator.joblib", "shap_explainer.joblib", "background_sample.joblib"]:
            joblib.dump(joblib.load(os.path.join(version_dir, fname)), os.path.join(self.registry_dir, fname))

        with open(os.path.join(self.registry_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return version_dir

    def load_model_package(self, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Loads versioned model artifacts and metadata.
        """
        target_dir = os.path.join(self.registry_dir, version) if version else self.registry_dir

        model_path = os.path.join(target_dir, "model.joblib")
        calib_path = os.path.join(target_dir, "calibrator.joblib")
        shap_path = os.path.join(target_dir, "shap_explainer.joblib")
        bg_path = os.path.join(target_dir, "background_sample.joblib")
        meta_path = os.path.join(target_dir, "metadata.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found at {model_path}")
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata file not found at {meta_path}")

        model = joblib.load(model_path)
        calibrator = joblib.load(calib_path)
        shap_explainer = joblib.load(shap_path)
        background_sample = joblib.load(bg_path)

        with open(meta_path, "r") as f:
            metadata = json.load(f)

        self.validate_metadata(metadata)

        prep_path = os.path.join(target_dir, "preprocessor.joblib")
        preprocessor = joblib.load(prep_path) if os.path.exists(prep_path) else None

        return {
            "model": model,
            "calibrator": calibrator,
            "shap_explainer": shap_explainer,
            "background_sample": background_sample,
            "preprocessor": preprocessor,
            "metadata": metadata
        }

    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]):
        """
        Ensures all required metadata fields are present and valid.
        """
        for key in REQUIRED_METADATA_KEYS:
            if key not in metadata:
                raise ValueError(f"Missing required metadata key: '{key}'")
            if metadata[key] is None:
                raise ValueError(f"Metadata key '{key}' cannot be None")

        if not isinstance(metadata["feature_names"], list) or len(metadata["feature_names"]) == 0:
            raise ValueError("Metadata 'feature_names' must be a non-empty list.")

    @staticmethod
    def check_feature_compatibility(input_features: List[str], expected_features: List[str]) -> bool:
        """
        Validates feature vector compatibility.
        """
        if list(input_features) != list(expected_features):
            missing = set(expected_features) - set(input_features)
            extra = set(input_features) - set(expected_features)
            raise ValueError(f"Feature incompatibility detected! Missing: {missing}, Unexpected extra: {extra}")
        return True
