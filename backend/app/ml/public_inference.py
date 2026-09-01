import os
import sys
import json
import joblib
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

DEFAULT_PUBLIC_ARTIFACTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "artifacts", "public", "v1.0.0")
)

PUBLIC_FEATURE_NAMES = [
    "Time", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10",
    "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18", "V19", "V20",
    "V21", "V22", "V23", "V24", "V25", "V26", "V27", "V28", "Amount"
]

class PublicInferenceService:
    """
    Inference service for the frozen Public Benchmark Pipeline.
    
    Guarantees:
    - Loads frozen XGBoost model, StandardScaler preprocessor, and ProbabilityCalibrator.
    - Preprocesses input dictionary containing 30 native public features.
    - Computes raw prediction, applies frozen isotonic calibrator, evaluates fixed 0.5 decision threshold.
    - NEVER calls model.fit(), preprocessor.fit(), or calibrator.fit().
    - Never accesses test set labels or predictions.
    """

    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = artifacts_dir or DEFAULT_PUBLIC_ARTIFACTS_DIR
        self._load_artifacts()

    def _load_artifacts(self):
        model_path = os.path.join(self.artifacts_dir, "model.joblib")
        preprocessor_path = os.path.join(self.artifacts_dir, "preprocessor.joblib")
        calibrator_path = os.path.join(self.artifacts_dir, "calibrator.joblib")
        metadata_path = os.path.join(self.artifacts_dir, "metadata.json")

        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path) or not os.path.exists(calibrator_path):
            raise FileNotFoundError(f"Public benchmark artifacts missing in '{self.artifacts_dir}'. Complete Steps 15 and 16 first.")

        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)
        self.calibrator = joblib.load(calibrator_path)

        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

        self.model_version = self.metadata.get("model_version", "v1.0.0")
        self.dataset_source = "public"
        self.dataset_type = "Public benchmark — locally supplied dataset"
        self.threshold = 0.5
        self.threshold_source = "fixed_default_0.5"
        self.calibration_method = getattr(self.calibrator, "selected_method", "isotonic")
        self.feature_columns = PUBLIC_FEATURE_NAMES
        self._shap_explainer = None

    @property
    def shap_explainer(self):
        if self._shap_explainer is None:
            import shap
            self._shap_explainer = shap.TreeExplainer(self.model)
        return self._shap_explainer

    def predict(self, input_data: Dict[str, Any], include_explanations: bool = False) -> Dict[str, Any]:
        """
        Executes inference for a single public transaction feature input.
        """
        # Validate missing features
        missing_features = [col for col in PUBLIC_FEATURE_NAMES if col not in input_data]
        if missing_features:
            raise ValueError(f"Missing required public benchmark feature(s): {missing_features}")

        # Extract features in strict schema order
        row_dict = {col: float(input_data[col]) for col in PUBLIC_FEATURE_NAMES}
        df_input = pd.DataFrame([row_dict], columns=PUBLIC_FEATURE_NAMES)

        # Step 1: Preprocess (Transform ONLY using frozen scaler)
        X_scaled = pd.DataFrame(self.preprocessor.transform(df_input), columns=PUBLIC_FEATURE_NAMES)

        # Step 2: Prediction (Frozen XGBoost model)
        raw_prob = float(self.model.predict_proba(X_scaled)[0, 1])

        # Step 3: Calibration (Frozen Isotonic Calibrator)
        calibrated_prob = float(self.calibrator.predict([raw_prob])[0])

        # Step 4: Decision (Fixed 0.5 threshold)
        decision = "FRAUD" if calibrated_prob >= self.threshold else "LEGITIMATE"

        response = {
            "model_version": self.model_version,
            "dataset_source": self.dataset_source,
            "dataset_type": self.dataset_type,
            "raw_probability": round(raw_prob, 4),
            "calibrated_probability": round(calibrated_prob, 4),
            "threshold": self.threshold,
            "threshold_source": self.threshold_source,
            "calibration_method": self.calibration_method,
            "decision": decision
        }

        # Step 5: Optional SHAP local explanations
        if include_explanations:
            shap_vals = self.shap_explainer.shap_values(X_scaled)
            if isinstance(shap_vals, list):
                row_shap = shap_vals[1][0]
            elif len(shap_vals.shape) == 3:
                row_shap = shap_vals[0, :, 1]
            else:
                row_shap = shap_vals[0]

            pos_features = []
            neg_features = []

            for idx, feature_name in enumerate(PUBLIC_FEATURE_NAMES):
                val_shap = float(row_shap[idx])
                feat_val = float(df_input.iloc[0][feature_name])
                feat_type = "Transaction Amount ($)" if feature_name == "Amount" else ("Relative Time Offset (sec)" if feature_name == "Time" else "PCA-transformed component")
                
                item = {
                    "feature": feature_name,
                    "feature_type": feat_type,
                    "feature_value": round(feat_val, 4),
                    "shap_value": round(val_shap, 4),
                    "direction": "INCREASES_FRAUD_RISK" if val_shap > 0 else "REDUCES_FRAUD_RISK"
                }

                if val_shap > 0:
                    pos_features.append(item)
                elif val_shap < 0:
                    neg_features.append(item)

            pos_features.sort(key=lambda x: x["shap_value"], reverse=True)
            neg_features.sort(key=lambda x: x["shap_value"])

            response["top_positive_features"] = pos_features[:5]
            response["top_negative_features"] = neg_features[:5]

        return response

public_inference_service = PublicInferenceService()
