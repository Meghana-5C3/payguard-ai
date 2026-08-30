import os
import sys
import json
import joblib
from datetime import datetime, timezone
from typing import Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

import xgboost as xgb
import shap

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.ml.datasets.registry import get_dataset
from backend.app.ml.synthetic_data import FEATURE_NAMES as SYNTHETIC_FEATURE_NAMES
from backend.app.ml.split import split_dataset
from backend.app.ml.leakage_checks import leakage_checker
from backend.app.ml.calibrator import ProbabilityCalibrator
from backend.app.ml.evaluator import ModelEvaluator
from backend.app.ml.model_registry import ModelRegistry

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

def train_and_save_pipeline(
    artifacts_dir: str,
    version: str = "v1.0.0",
    dataset_source: Optional[str] = None,
    public_csv_path: Optional[str] = None,
    public_target_column: Optional[str] = None
):
    """
    Clean 8-Step ML Pipeline supporting both Synthetic Demo and Public Dataset Adapter:
    Step 1: Dataset loading via Dataset Registry (Synthetic or Public)
    Step 2: Pre-split validation & strict 70/15/15 split
    Step 3: Data leakage checks
    Step 4: Preprocessing (fitted on X_train ONLY)
    Step 5: Model training (XGBoost on X_train ONLY)
    Step 6: Validation evaluation & Calibration selection (Isotonic vs Sigmoid on X_val ONLY)
    Step 7: Final test evaluation (Evaluated via ModelEvaluator ONCE on untouched X_test ONLY)
    Step 8: Save versioned model package & metadata via ModelRegistry & export model_metrics.json
    """
    seed = 42

    # Resolve environment variables / parameters with fallback
    effective_source = (dataset_source or os.environ.get("DATASET_SOURCE", "synthetic")).lower().strip()
    effective_public_path = public_csv_path or os.environ.get("PUBLIC_DATASET_PATH")
    effective_target_col = public_target_column or os.environ.get("PUBLIC_TARGET_COLUMN", "Class")

    if effective_source == "public":
        if not effective_public_path:
            raise ValueError("Public dataset configuration error: PUBLIC_DATASET_PATH environment variable or public_csv_path argument is required when DATASET_SOURCE=public.")
        if not os.path.exists(effective_public_path):
            raise ValueError(f"Public dataset configuration error: Local CSV file not found at '{effective_public_path}'.")

    # Isolate output directory for public vs synthetic datasets
    if effective_source == "public":
        effective_artifacts_dir = os.path.join(artifacts_dir, "public")
    else:
        effective_artifacts_dir = artifacts_dir

    os.makedirs(effective_artifacts_dir, exist_ok=True)

    # Step 1: Dataset loading via Dataset Registry
    print(f"[ML Pipeline Step 1] Loading dataset adapter (source='{effective_source}')...")
    dataset_pkg = get_dataset(
        source=effective_source,
        csv_path=effective_public_path,
        target_column=effective_target_col,
        n_samples=25000,
        seed=seed
    )

    df = dataset_pkg.dataframe
    feature_names = dataset_pkg.feature_columns
    target_name = dataset_pkg.target_column

    print(f"[ML Pipeline Data Stats] Source: {dataset_pkg.dataset_source} | Type: {dataset_pkg.dataset_type}")
    print(f"[ML Pipeline Data Stats] Total: {dataset_pkg.sample_count:,} | Fraud: {dataset_pkg.fraud_count:,} ({dataset_pkg.fraud_rate * 100:.2f}%)")

    # Step 2: Strict 70% Train, 15% Validation, 15% Test split
    print("[ML Pipeline Step 2] Splitting dataset into 70% Train, 15% Val, 15% Test...")
    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(
        df=df,
        feature_names=feature_names,
        target_name=target_name,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        seed=seed,
        stratify=True
    )
    print(f"[ML Pipeline Split Sizes] Train={len(X_train):,}, Val={len(X_val):,}, Test={len(X_test):,}")

    # Step 3: Pre-split validation and leakage checks
    print("[ML Pipeline Step 3] Running Data Leakage Validation Layer...")
    preprocessor_check = StandardScaler()
    preprocessor_check.fit(X_train)  # Fitted on X_train ONLY

    leakage_report = leakage_checker.run_all_checks(
        df=df,
        feature_names=feature_names,
        target_name=target_name,
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        preprocessor=preprocessor_check
    )

    if not leakage_report["passed"]:
        print(f"[ML Pipeline ERROR] Data Leakage Check Failed! Errors: {leakage_report['errors']}")
        raise RuntimeError(f"Training aborted due to Data Leakage Check Failure: {leakage_report['errors']}")

    print("[ML Pipeline PASSED] 0 Critical Leakage Errors Detected.")

    # Step 4: Preprocessing (fitted on X_train ONLY)
    print("[ML Pipeline Step 4] Fitting Preprocessor on Training Set ONLY...")
    preprocessor = StandardScaler()
    preprocessor.fit(X_train)

    # Step 5: Model training (XGBoost on X_train ONLY)
    print("[ML Pipeline Step 5] Training XGBoost Classifier on Training Set...")
    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=(len(y_train) - sum(y_train)) / max(1, sum(y_train)),
        random_state=seed,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)

    # Step 6: Validation evaluation & Calibration selection (X_val ONLY)
    print("[ML Pipeline Step 6] Fitting ProbabilityCalibrator on Validation Set predictions ONLY...")
    raw_val_probs = model.predict_proba(X_val)[:, 1]
    calibrator = ProbabilityCalibrator(method="auto")
    calib_val_report = calibrator.fit(raw_val_probs, y_val.values)
    print(f"[ML Pipeline Calibration] Selected Method: '{calibrator.selected_method}' (Val Brier: {calib_val_report['calibrated_brier']:.4f}, Val ECE: {calib_val_report['calibrated_ece']:.4f})")

    # Step 7: Final test evaluation (Frozen pipeline evaluated ONCE on untouched X_test ONLY via ModelEvaluator)
    print("[ML Pipeline Step 7] Evaluating Frozen Pipeline on Untouched Test Set ONLY via ModelEvaluator...")
    raw_test_probs = model.predict_proba(X_test)[:, 1]
    calibrated_test_probs = calibrator.predict(raw_test_probs)

    eval_report = ModelEvaluator.evaluate_performance(
        y_true=y_test.values,
        y_prob=calibrated_test_probs,
        threshold=0.5,
        model_version=version,
        dataset_source=dataset_pkg.dataset_source,
        dataset_type=dataset_pkg.dataset_type
    )

    test_metrics = eval_report["metrics"]
    print(f"[ML Pipeline Final Evaluation] ROC-AUC: {test_metrics['roc_auc']} | PR-AUC: {test_metrics['pr_auc']} | Brier: {test_metrics['brier']} | ECE: {test_metrics['ece']}")

    # Build SHAP TreeExplainer
    print("[ML Pipeline] Initializing SHAP TreeExplainer...")
    explainer = shap.TreeExplainer(model)
    background_sample = X_train.sample(n=min(100, len(X_train)), random_state=seed)

    # Build feature labels for global importance
    feat_labels = {f: FEATURE_LABELS.get(f, f) for f in feature_names}

    # Step 8: Save versioned model artifact & metadata via ModelRegistry
    print("[ML Pipeline Step 8] Registering versioned model package via ModelRegistry...")
    metadata = {
        "model_version": version,
        "feature_version": "v1.0",
        "dataset_source": dataset_pkg.dataset_source,
        "dataset_type": dataset_pkg.dataset_type,
        "dataset_size": dataset_pkg.sample_count,
        "fraud_count": dataset_pkg.fraud_count,
        "fraud_rate": round(dataset_pkg.fraud_rate, 4),
        "dataset_version": "v1.0",
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "feature_names": feature_names,
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test),
        "training_sample_count": len(X_train),
        "validation_sample_count": len(X_val),
        "test_sample_count": len(X_test),
        "fraud_prevalence": round(dataset_pkg.fraud_rate, 4),
        "model_type": f"XGBoost + {calibrator.selected_method.title()} Calibration",
        "calibration_method": calibrator.selected_method,
        "roc_auc": test_metrics["roc_auc"],
        "pr_auc": test_metrics["pr_auc"],
        "brier_score_raw": calib_val_report["raw_brier"],
        "brier_score_calibrated": test_metrics["brier"],
        "ece_raw": calib_val_report["raw_ece"],
        "ece_calibrated": test_metrics["ece"],
        "precision": test_metrics["precision"],
        "recall": test_metrics["recall"],
        "f1_score": test_metrics["f1"],
        "confusion_matrix": eval_report["confusion_matrix"],
        "calibration_curve": eval_report["calibration_curve"],
        "precision_recall_curve": eval_report["precision_recall_curve"],
        "roc_curve": eval_report["roc_curve"],
        "global_feature_importance": [
            {"feature": name, "label": feat_labels[name], "importance": round(float(imp), 4)}
            for name, imp in sorted(zip(feature_names, model.feature_importances_), key=lambda x: x[1], reverse=True)
        ],
        "feature_labels": feat_labels,
        "leakage_report": leakage_report
    }

    registry = ModelRegistry(effective_artifacts_dir)
    version_dir = registry.save_model_package(
        model=model,
        calibrator=calibrator,
        shap_explainer=explainer,
        background_sample=background_sample,
        metadata=metadata,
        preprocessor=preprocessor,
        version=version
    )

    with open(os.path.join(effective_artifacts_dir, "metrics.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Save model_metrics.json in artifacts root and version dir
    ModelEvaluator.save_metrics(eval_report, os.path.join(effective_artifacts_dir, "model_metrics.json"))
    ModelEvaluator.save_metrics(eval_report, os.path.join(version_dir, "model_metrics.json"))

    print(f"[ML Pipeline SUCCESS] Versioned model artifacts and model_metrics.json saved to: {version_dir}")

if __name__ == "__main__":
    artifacts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "artifacts"))
    train_and_save_pipeline(artifacts_path, version="v1.0.0")
