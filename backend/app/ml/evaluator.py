import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_recall_fscore_support,
    brier_score_loss,
    confusion_matrix,
    roc_curve,
    precision_recall_curve
)
from backend.app.ml.calibrator import calculate_ece

class ModelEvaluator:
    """
    Production-quality evaluation module for transaction risk manager models.
    
    Guarantees:
    - Prioritizes PR-AUC and probabilistic calibration (Brier/ECE) over naive accuracy.
    - Computes 100% dynamic metrics from empirical test set ground truth and predictions.
    - Exports structured report to model_metrics.json.
    """

    @staticmethod
    def evaluate_performance(
        y_true: np.ndarray,
        y_prob: np.ndarray,
        threshold: float = 0.5,
        model_version: str = "v1.0.0",
        dataset_source: str = "Synthetic benchmark — generated dataset",
        dataset_type: str = "Synthetic benchmark — generated dataset"
    ) -> Dict[str, Any]:
        """
        Calculates ROC-AUC, PR-AUC, Precision, Recall, F1, Brier score, ECE,
        and generates downsampled curve points.
        """
        y_true = np.asarray(y_true, dtype=int)
        y_prob = np.asarray(y_prob, dtype=float)

        if len(y_true) != len(y_prob):
            raise ValueError("y_true and y_prob must have identical lengths.")

        # 1. Primary imbalanced and calibration metrics
        has_two_classes = len(np.unique(y_true)) > 1
        roc_auc = float(roc_auc_score(y_true, y_prob)) if has_two_classes else 0.5
        pr_auc = float(average_precision_score(y_true, y_prob)) if has_two_classes else 0.0
        brier = float(brier_score_loss(y_true, y_prob))
        ece, calib_curve = calculate_ece(y_true, y_prob)

        y_pred = (y_prob >= threshold).astype(int)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
        cm = confusion_matrix(y_true, y_pred).tolist()

        # 2. ROC curve downsampled points
        if has_two_classes:
            fpr, tpr, _ = roc_curve(y_true, y_prob)
            step_roc = max(1, len(fpr) // 25)
            roc_curve_points = [
                {"fpr": round(float(f), 4), "tpr": round(float(t), 4)}
                for f, t in zip(fpr[::step_roc], tpr[::step_roc])
            ]

            # 3. Precision-Recall curve downsampled points
            precisions, recalls, _ = precision_recall_curve(y_true, y_prob)
            step_pr = max(1, len(precisions) // 25)
            pr_curve_points = [
                {"precision": round(float(p), 4), "recall": round(float(r), 4)}
                for p, r in zip(precisions[::step_pr], recalls[::step_pr])
            ]
        else:
            roc_curve_points = []
            pr_curve_points = []

        report = {
            "model_version": model_version,
            "dataset_source": dataset_source,
            "dataset_type": dataset_type,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "roc_auc": round(roc_auc, 4),
                "pr_auc": round(pr_auc, 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1": round(float(f1), 4),
                "brier": round(brier, 4),
                "ece": round(ece, 4)
            },
            "confusion_matrix": {
                "true_negatives": cm[0][0],
                "false_positives": cm[0][1] if len(cm[0]) > 1 else 0,
                "false_negatives": cm[1][0] if len(cm) > 1 else 0,
                "true_positives": cm[1][1] if len(cm) > 1 and len(cm[1]) > 1 else 0,
            },
            "roc_curve": roc_curve_points,
            "precision_recall_curve": pr_curve_points,
            "calibration_curve": calib_curve
        }
        return report

    @staticmethod
    def save_metrics(report: Dict[str, Any], filepath: str):
        """
        Saves evaluation report dictionary to JSON file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
