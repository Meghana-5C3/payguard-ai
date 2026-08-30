import os
import sys
import json
import joblib
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.ml.datasets.registry import get_dataset
from backend.app.ml.datasets.public_preprocessor import prepare_public_features
from backend.app.ml.split import split_dataset
from backend.app.ml.calibrator import calculate_ece
from backend.app.ml.evaluator import ModelEvaluator

DEFAULT_PUBLIC_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_fraud_dataset.csv", "creditcard.csv")
)

def evaluate_public_benchmark(
    artifacts_dir: Optional[str] = None,
    csv_path: Optional[str] = None,
    target_column: str = "Class",
    version: str = "v1.0.0",
    seed: int = 42,
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Step 17: Final Public Benchmark Evaluation on Untouched Held-Out Test Set.
    
    Guarantees:
    - Loads frozen public model, preprocessor, and calibrator.
    - Reconstructs strict 70% Train, 15% Val, 15% Test split.
    - Evaluates performance ONCE on untouched X_test / y_test ONLY.
    - NEVER fits or modifies model, preprocessor, or calibrator.
    - Saves artifacts to backend/app/ml/artifacts/public/v1.0.0/model_metrics.json.
    - Preserves synthetic artifacts completely untouched.
    """
    effective_path = csv_path or os.environ.get("PUBLIC_DATASET_PATH", DEFAULT_PUBLIC_CSV_PATH)
    effective_target = target_column or os.environ.get("PUBLIC_TARGET_COLUMN", "Class")

    if not os.path.exists(effective_path):
        raise ValueError(f"Public dataset configuration error: Local CSV file not found at '{effective_path}'.")

    if artifacts_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "artifacts"))
        public_artifacts_dir = os.path.join(base_dir, "public")
    else:
        public_artifacts_dir = os.path.join(artifacts_dir, "public") if not artifacts_dir.endswith("public") else artifacts_dir

    version_dir = os.path.join(public_artifacts_dir, version)

    # 1. Load frozen components
    model_path = os.path.join(version_dir, "model.joblib")
    preprocessor_path = os.path.join(version_dir, "preprocessor.joblib")
    calibrator_path = os.path.join(version_dir, "calibrator.joblib")

    if not all(os.path.exists(p) for p in [model_path, preprocessor_path, calibrator_path]):
        raise FileNotFoundError(f"Frozen public pipeline components missing in '{version_dir}'. Complete Steps 15 and 16 first.")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    calibrator = joblib.load(calibrator_path)

    # 2. Reconstruct original test split (70% Train, 15% Val, 15% Test stratified)
    dataset_res = get_dataset(source="public", csv_path=effective_path, target_column=effective_target)
    prep_data = prepare_public_features(dataset_res)
    df = prep_data.X.copy()
    df[effective_target] = prep_data.y.values
    feature_names = prep_data.feature_columns

    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(
        df=df,
        feature_names=feature_names,
        target_name=effective_target,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        seed=seed,
        stratify=True
    )

    # 3. Generate raw test probabilities & apply frozen calibrator
    X_test_scaled = preprocessor.transform(X_test)
    raw_test_probs = model.predict_proba(X_test_scaled)[:, 1]
    calibrated_test_probs = calibrator.predict(raw_test_probs)

    # Calculate raw vs calibrated metrics on test set for descriptive comparison
    raw_test_brier = float(brier_score_loss(y_test, raw_test_probs))
    raw_test_ece, _ = calculate_ece(y_test.values, raw_test_probs)

    # 4. Evaluate final performance using ModelEvaluator
    eval_report = ModelEvaluator.evaluate_performance(
        y_true=y_test.values,
        y_prob=calibrated_test_probs,
        threshold=threshold,
        model_version=version,
        dataset_source="public",
        dataset_type="Public benchmark — locally supplied dataset"
    )

    metrics = eval_report["metrics"]
    cm = eval_report["confusion_matrix"]

    full_metrics_artifact = {
        "model_version": version,
        "dataset_source": "public",
        "dataset_type": "Public benchmark — locally supplied dataset",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_size": dataset_res.sample_count,
        "test_size": len(X_test),
        "fraud_count_total": dataset_res.fraud_count,
        "fraud_count_test": int(y_test.sum()),
        "fraud_rate_total": round(dataset_res.fraud_rate, 4),
        "threshold": threshold,
        "threshold_source": "fixed_default_0.5",
        "metrics": metrics,
        "confusion_matrix": cm,
        "calibration_comparison": {
            "raw_brier": round(raw_test_brier, 4),
            "calibrated_brier": metrics["brier"],
            "raw_ece": round(raw_test_ece, 4),
            "calibrated_ece": metrics["ece"]
        },
        "roc_curve": eval_report["roc_curve"],
        "precision_recall_curve": eval_report["precision_recall_curve"],
        "calibration_curve": eval_report["calibration_curve"]
    }

    # Save to version_dir and public_artifacts_dir
    ModelEvaluator.save_metrics(full_metrics_artifact, os.path.join(version_dir, "model_metrics.json"))
    ModelEvaluator.save_metrics(full_metrics_artifact, os.path.join(public_artifacts_dir, "model_metrics.json"))

    # Update metadata.json with final metrics
    metadata_path = os.path.join(version_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {}

    metadata.update({
        "final_test_metrics": metrics,
        "confusion_matrix": cm,
        "calibration_comparison": full_metrics_artifact["calibration_comparison"],
        "evaluated_at": full_metrics_artifact["evaluated_at"]
    })

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    with open(os.path.join(public_artifacts_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Public ML Pipeline SUCCESS] Final evaluation metrics saved to: {os.path.join(version_dir, 'model_metrics.json')}")
    return full_metrics_artifact

if __name__ == "__main__":
    evaluate_public_benchmark()
