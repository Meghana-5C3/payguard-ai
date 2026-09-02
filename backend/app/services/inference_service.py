import os
import joblib
import pandas as pd
import numpy as np
from backend.app.models import FeatureVector

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts"))

FEATURE_NAMES = [
    "amount",
    "tx_amount_zscore",
    "tx_velocity_1h",
    "tx_velocity_24h",
    "tx_amount_sum_24h",
    "is_new_device",
    "is_cross_border",
    "time_since_last_tx_sec",
    "distance_from_home_km",
    "mcc_risk_tier",
    "ip_reputation_score",
    "failed_otp_attempts_24h",
]

class InferenceService:
    def __init__(self):
        self.model = None
        self.calibrator = None
        self.artifacts_dir = None
        self.load_artifacts()

    def load_artifacts(self):
        possible_dirs = [
            ARTIFACTS_DIR,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "app", "ml", "artifacts")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app", "ml", "artifacts")),
            "/var/task/backend/app/ml/artifacts",
        ]
        target_dir = None
        for d in possible_dirs:
            if d and os.path.exists(os.path.join(d, "model.joblib")) and os.path.exists(os.path.join(d, "calibrator.joblib")):
                target_dir = d
                break

        if target_dir is not None:
            self.artifacts_dir = target_dir
            self.model = joblib.load(os.path.join(target_dir, "model.joblib"))
            self.calibrator = joblib.load(os.path.join(target_dir, "calibrator.joblib"))
            print(f"[InferenceService] Model and Calibrator loaded successfully from '{target_dir}'.")
        else:
            print(f"[InferenceService] WARNING: Model artifacts not found in candidate paths: {possible_dirs}")

    def predict(self, feature_vector: FeatureVector):
        if self.model is None or self.calibrator is None:
            self.load_artifacts()

        if self.model is None or self.calibrator is None:
            raise RuntimeError("[InferenceService] Cannot execute predict(): Model or Calibrator artifact is missing.")

        row = {
            "amount": feature_vector.amount,
            "tx_amount_zscore": feature_vector.tx_amount_zscore,
            "tx_velocity_1h": feature_vector.tx_velocity_1h,
            "tx_velocity_24h": feature_vector.tx_velocity_24h,
            "tx_amount_sum_24h": feature_vector.tx_amount_sum_24h,
            "is_new_device": feature_vector.is_new_device,
            "is_cross_border": feature_vector.is_cross_border,
            "time_since_last_tx_sec": feature_vector.time_since_last_tx_sec,
            "distance_from_home_km": feature_vector.distance_from_home_km,
            "mcc_risk_tier": feature_vector.mcc_risk_tier,
            "ip_reputation_score": feature_vector.ip_reputation_score,
            "failed_otp_attempts_24h": feature_vector.failed_otp_attempts_24h,
        }

        X_df = pd.DataFrame([row])[FEATURE_NAMES]

        # Raw Model Probability
        raw_prob = float(self.model.predict_proba(X_df)[0, 1])

        # Calibrated Probability via Isotonic Regression
        calibrated_prob = float(self.calibrator.predict([raw_prob])[0])
        calibrated_prob = max(0.0001, min(0.9999, calibrated_prob))

        # Risk Score (0-1000)
        risk_score = int(round(calibrated_prob * 1000.0))

        if risk_score < 250:
            risk_level = "LOW"
        elif risk_score < 650:
            risk_level = "MEDIUM"
        elif risk_score < 850:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        return {
            "raw_probability": round(raw_prob, 4),
            "calibrated_probability": round(calibrated_prob, 4),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "X_df": X_df
        }

inference_service = InferenceService()
