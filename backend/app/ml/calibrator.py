from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

def calculate_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Computes Expected Calibration Error (ECE) and bin details across 10 deciles.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    bin_details = []

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (y_prob >= bin_lower) & (y_prob < bin_upper)
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(y_true[in_bin])
            avg_confidence_in_bin = np.mean(y_prob[in_bin])
            ece += np.abs(accuracy_in_bin - avg_confidence_in_bin) * prop_in_bin
            bin_details.append({
                "bin_lower": round(float(bin_lower), 2),
                "bin_upper": round(float(bin_upper), 2),
                "count": int(np.sum(in_bin)),
                "actual_rate": round(float(accuracy_in_bin), 4),
                "predicted_prob": round(float(avg_confidence_in_bin), 4),
            })

    return float(ece), bin_details

class ProbabilityCalibrator:
    """
    Probability Calibration Layer supporting Isotonic Regression and Platt (Sigmoid) Scaling.
    
    Rules:
    - Calibration is fitted ONLY on validation set predictions (never on test set).
    - Dynamically evaluates Isotonic Regression vs Platt Scaling on validation Brier/ECE scores.
    - Selects Isotonic Regression when sample size is large (N >= 1000, positive count >= 30)
      and produces lower Brier score; falls back to Platt Scaling otherwise.
    - Freezes model once selected.
    """

    def __init__(self, method: str = "auto", min_isotonic_samples: int = 1000, min_positive_samples: int = 30):
        self.method = method  # "auto", "isotonic", "sigmoid"
        self.min_isotonic_samples = min_isotonic_samples
        self.min_positive_samples = min_positive_samples
        self.selected_method: Optional[str] = None
        self.calibrator_model: Any = None

    def fit(self, val_raw_probs: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """
        Fits calibration models on validation predictions ONLY.
        """
        val_raw_probs = np.asarray(val_raw_probs)
        y_val = np.asarray(y_val)

        raw_brier = float(brier_score_loss(y_val, val_raw_probs))
        raw_ece, raw_bins = calculate_ece(y_val, val_raw_probs)

        # 1. Fit Isotonic Regression
        iso_calib = IsotonicRegression(out_of_bounds="clip", y_min=0.0001, y_max=0.9999)
        iso_calib.fit(val_raw_probs, y_val)
        iso_val_probs = iso_calib.predict(val_raw_probs)
        iso_brier = float(brier_score_loss(y_val, iso_val_probs))
        iso_ece, _ = calculate_ece(y_val, iso_val_probs)

        # 2. Fit Platt / Sigmoid Scaling
        clip_probs = np.clip(val_raw_probs, 1e-6, 1 - 1e-6)
        logits = np.log(clip_probs / (1.0 - clip_probs)).reshape(-1, 1)
        sig_calib = LogisticRegression(C=1.0, solver="lbfgs")
        sig_calib.fit(logits, y_val)
        sig_val_probs = sig_calib.predict_proba(logits)[:, 1]
        sig_brier = float(brier_score_loss(y_val, sig_val_probs))
        sig_ece, _ = calculate_ece(y_val, sig_val_probs)

        # Selection logic
        n_samples = len(y_val)
        n_positives = int(np.sum(y_val == 1))

        if self.method in ["isotonic", "sigmoid"]:
            chosen = self.method
        else:
            if n_samples >= self.min_isotonic_samples and n_positives >= self.min_positive_samples:
                chosen = "isotonic" if iso_brier <= sig_brier else "sigmoid"
            else:
                chosen = "sigmoid"

        self.selected_method = chosen
        if chosen == "isotonic":
            self.calibrator_model = iso_calib
        else:
            self.calibrator_model = sig_calib

        calib_val_probs = self.predict(val_raw_probs)
        calib_brier = float(brier_score_loss(y_val, calib_val_probs))
        calib_ece, calib_bins = calculate_ece(y_val, calib_val_probs)

        return {
            "selected_method": self.selected_method,
            "raw_brier": raw_brier,
            "raw_ece": raw_ece,
            "isotonic_brier": iso_brier,
            "isotonic_ece": iso_ece,
            "sigmoid_brier": sig_brier,
            "sigmoid_ece": sig_ece,
            "calibrated_brier": calib_brier,
            "calibrated_ece": calib_ece,
            "calibration_curve_val": calib_bins
        }

    def predict(self, raw_probs: np.ndarray) -> np.ndarray:
        """
        Transforms raw probabilities into calibrated probabilities.
        Returns output strictly bounded between 0.0001 and 0.9999.
        """
        raw_probs = np.asarray(raw_probs)
        if self.calibrator_model is None:
            raise RuntimeError("ProbabilityCalibrator is not fitted yet!")

        if self.selected_method == "isotonic":
            calibrated = self.calibrator_model.predict(raw_probs)
        else:
            clip_probs = np.clip(raw_probs, 1e-6, 1 - 1e-6)
            logits = np.log(clip_probs / (1.0 - clip_probs)).reshape(-1, 1)
            calibrated = self.calibrator_model.predict_proba(logits)[:, 1]

        return np.clip(calibrated, 0.0001, 0.9999)
