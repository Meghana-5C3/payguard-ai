import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts"))

FEATURE_LABELS = {
    "amount": "Transaction Amount ($)",
    "tx_amount_zscore": "Amount Z-Score vs 30D Mean",
    "tx_velocity_1h": "1-Hour Velocity Count",
    "tx_velocity_24h": "24-Hour Velocity Count",
    "tx_amount_sum_24h": "24-Hour Cumulative Spend ($)",
    "is_new_device": "Unrecognized Device Fingerprint",
    "is_cross_border": "Cross-Border Transaction",
    "time_since_last_tx_sec": "Time Since Last Transaction (sec)",
    "distance_from_home_km": "Distance from Home (km)",
    "mcc_risk_tier": "Merchant Risk Tier (1-5)",
    "ip_reputation_score": "IP Anonymity / Risk Score (0-100)",
    "failed_otp_attempts_24h": "Failed OTP Attempts (24h)",
}

class ShapService:
    def __init__(self):
        self.explainer = None

    def load_explainer(self):
        if self.explainer is not None:
            return
        possible_dirs = [
            ARTIFACTS_DIR,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "app", "ml", "artifacts")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app", "ml", "artifacts")),
            "/var/task/backend/app/ml/artifacts",
        ]
        target_dir = None
        for d in possible_dirs:
            if d and os.path.exists(os.path.join(d, "shap_explainer.joblib")):
                target_dir = d
                break

        if target_dir is not None:
            try:
                self.explainer = joblib.load(os.path.join(target_dir, "shap_explainer.joblib"))
                print(f"[ShapService] SHAP TreeExplainer loaded successfully from '{target_dir}'.")
            except Exception as e:
                print(f"[ShapService] Note: Using XGBoost native TreeSHAP calculation ({e}).")
                self.explainer = None
        else:
            print("[ShapService] Note: Using XGBoost native TreeSHAP calculation.")

    def explain(self, X_df: pd.DataFrame) -> Dict[str, Any]:
        if self.explainer is None:
            self.load_explainer()

        if self.explainer is not None:
            shap_values = self.explainer(X_df)
            values = shap_values.values[0] # 1D numpy array of SHAP attributions
        else:
            from backend.app.services.inference_service import inference_service
            import xgboost as xgb
            dmat = xgb.DMatrix(X_df)
            contribs = inference_service.model.get_booster().predict(dmat, pred_contribs=True)[0]
            values = contribs[:-1]

        attributions = []
        for feature_name, raw_shap_val in zip(X_df.columns, values):
            feat_val = X_df[feature_name].values[0]
            label = FEATURE_LABELS.get(feature_name, feature_name)
            
            direction = "INCREASES_RISK" if raw_shap_val > 0 else "REDUCES_RISK"
            impact_sign = f"+{raw_shap_val:.3f}" if raw_shap_val > 0 else f"{raw_shap_val:.3f}"

            # Domain human-readable description builder
            desc = self._build_feature_description(feature_name, feat_val, raw_shap_val)

            attributions.append({
                "feature": feature_name,
                "label": label,
                "value": feat_val if not isinstance(feat_val, (np.bool_, np.integer, np.floating)) else float(feat_val) if isinstance(feat_val, np.floating) else int(feat_val),
                "impact": impact_sign,
                "raw_shap_value": round(float(raw_shap_val), 4),
                "direction": direction,
                "description": desc
            })

        # Sort by absolute SHAP value magnitude
        attributions.sort(key=lambda x: abs(x["raw_shap_value"]), reverse=True)

        top_risk_drivers = [a for a in attributions if a["direction"] == "INCREASES_RISK"][:3]
        top_risk_mitigators = [a for a in attributions if a["direction"] == "REDUCES_RISK"][:2]

        natural_summary = self._build_natural_language_summary(top_risk_drivers, top_risk_mitigators)

        return {
            "attributions": attributions,
            "top_drivers": top_risk_drivers,
            "top_mitigators": top_risk_mitigators,
            "natural_explanation": natural_summary
        }

    def _build_feature_description(self, feature: str, val: Any, shap_val: float) -> str:
        if feature == "tx_amount_zscore":
            if val > 2.0:
                return f"Amount is {val:.2f} standard deviations above user's normal baseline."
            elif val < 0:
                return f"Amount is lower than user's normal average ({val:.2f} std dev)."
            return f"Amount is within expected variation ({val:.2f} std dev)."

        elif feature == "tx_velocity_1h":
            if val > 2:
                return f"Rapid burst detected: {int(val)} transactions executed within 1 hour."
            return f"Normal transaction velocity ({int(val)} in 1 hour)."

        elif feature == "is_new_device":
            if int(val) == 1:
                return "Transaction originated from an unrecognized device fingerprint."
            return "Recognized device fingerprint in user history."

        elif feature == "is_cross_border":
            if int(val) == 1:
                return "International transaction initiated outside home country."
            return "Domestic transaction matching home region."

        elif feature == "ip_reputation_score":
            if val > 70:
                return f"High-risk IP address detected (Risk score {val:.1f}/100, proxy/TOR match)."
            return f"Standard residential/cellular IP reputation ({val:.1f}/100)."

        elif feature == "failed_otp_attempts_24h":
            if int(val) > 0:
                return f"{int(val)} recent failed authentication attempt(s) logged."
            return "No authentication failures recorded."

        elif feature == "mcc_risk_tier":
            if int(val) >= 4:
                return f"High-risk Merchant Category (MCC Tier {int(val)}: crypto/wire transfer/gaming)."
            return f"Low/Standard risk merchant category (MCC Tier {int(val)})."

        elif feature == "distance_from_home_km":
            if val > 100:
                return f"Transaction location is {val:.1f} km away from user's primary residence."
            return f"Transaction located close to home region ({val:.1f} km)."

        elif feature == "amount":
            return f"Raw transaction magnitude: ${val:,.2f} USD."

        return f"{FEATURE_LABELS.get(feature, feature)} = {val}."

    def _build_natural_language_summary(self, drivers: List[Dict], mitigators: List[Dict]) -> str:
        if not drivers:
            return "Transaction presents low risk. Operational features align with user baseline history."

        driver_texts = [d["description"] for d in drivers]
        summary = "Primary risk drivers: " + " ".join(driver_texts)
        if mitigators:
            mitigator_texts = [m["description"] for m in mitigators]
            summary += " Mitigating factors: " + " ".join(mitigator_texts)

        return summary

shap_service = ShapService()
