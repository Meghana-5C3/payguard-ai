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
        self.load_artifacts()

    def load_artifacts(self):
        model_path = os.path.join(ARTIFACTS_DIR, "model.joblib")
        calib_path = os.path.join(ARTIFACTS_DIR, "calibrator.joblib")
        if os.path.exists(model_path) and os.path.exists(calib_path):
            self.model = joblib.load(model_path)
            self.calibrator = joblib.load(calib_path)
            print("[InferenceService] Model and Calibrator loaded successfully.")
        else:
            print("[InferenceService] WARNING: Model artifacts not found! Run train.py first.")

    def predict(self, feature_vector: FeatureVector):
        if self.model is None or self.calibrator is None:
            self.load_artifacts()

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
