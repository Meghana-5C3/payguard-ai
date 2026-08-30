import os
import sys
import json
import joblib
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.ml.datasets.registry import get_dataset
from backend.app.ml.datasets.public_preprocessor import prepare_public_features
from backend.app.ml.split import split_dataset
from backend.app.ml.calibrator import ProbabilityCalibrator

DEFAULT_PUBLIC_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_fraud_dataset.csv", "creditcard.csv")
)

def calibrate_public_benchmark(
    artifacts_dir: Optional[str] = None,
    csv_path: Optional[str] = None,
    target_column: str = "Class",
    version: str = "v1.0.0",
    seed: int = 42
) -> Dict[str, Any]:
    """
    Step 16: Public Benchmark Probability Calibration.
    
    Guarantees:
    - Fits ProbabilityCalibrator using validation predictions (X_val, y_val ONLY).
    - NEVER uses test data (X_test, y_test) for calibration fitting or method selection.
    - Saves calibrator artifact to backend/app/ml/artifacts/public/v1.0.0/calibrator.joblib.
    - Does NOT overwrite synthetic calibration artifacts.
    - Does NOT evaluate final test performance metrics (reserved for Step 17).
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
    
    # 1. Load trained public model & preprocessor
    model_path = os.path.join(version_dir, "model.joblib")
    preprocessor_path = os.path.join(version_dir, "preprocessor.joblib")

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        raise FileNotFoundError(f"Public model artifacts not found at '{version_dir}'. Train public model first (Step 15).")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    # 2. Re-create strict dataset split (70% Train, 15% Val, 15% Test)
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

    # 3. Generate raw validation predictions ONLY
    X_val_scaled = preprocessor.transform(X_val)
    raw_val_probs = model.predict_proba(X_val_scaled)[:, 1]

    # 4. Compare calibration methods & fit calibrator on validation data ONLY
    print("[Public ML Pipeline] Fitting ProbabilityCalibrator on Validation Set predictions ONLY...")
    calibrator = ProbabilityCalibrator(method="auto")
    calib_report = calibrator.fit(raw_val_probs, y_val.values)

    val_sample_count = len(y_val)
    val_fraud_count = int(y_val.sum())

    print(f"[Public ML Pipeline Calibration] Selected Method: '{calibrator.selected_method}' (Val Brier: {calib_report['raw_brier']:.4f}->{calib_report['calibrated_brier']:.4f}, Val ECE: {calib_report['raw_ece']:.4f}->{calib_report['calibrated_ece']:.4f})")

    # 5. Save public calibrator separately
    joblib.dump(calibrator, os.path.join(version_dir, "calibrator.joblib"))
    joblib.dump(calibrator, os.path.join(public_artifacts_dir, "calibrator.joblib"))

    # 6. Update metadata
    metadata_path = os.path.join(version_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {}

    metadata.update({
        "calibration_method": calibrator.selected_method,
        "validation_sample_count": val_sample_count,
        "validation_fraud_count": val_fraud_count,
        "validation_brier_before": calib_report["raw_brier"],
        "validation_brier_after": calib_report["calibrated_brier"],
        "validation_ece_before": calib_report["raw_ece"],
        "validation_ece_after": calib_report["calibrated_ece"],
        "calibration_curve_val": calib_report["calibration_curve_val"],
        "calibrated_at": datetime.now(timezone.utc).isoformat()
    })

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    with open(os.path.join(public_artifacts_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Public ML Pipeline SUCCESS] Public calibrator saved to: {os.path.join(version_dir, 'calibrator.joblib')}")

    return {
        "version_dir": version_dir,
        "public_artifacts_dir": public_artifacts_dir,
        "selected_method": calibrator.selected_method,
        "val_sample_count": val_sample_count,
        "val_fraud_count": val_fraud_count,
        "raw_brier": calib_report["raw_brier"],
        "calibrated_brier": calib_report["calibrated_brier"],
        "raw_ece": calib_report["raw_ece"],
        "calibrated_ece": calib_report["calibrated_ece"],
        "calibrator": calibrator
    }

if __name__ == "__main__":
    calibrate_public_benchmark()
