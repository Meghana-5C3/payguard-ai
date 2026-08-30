import os
import sys
import json
import joblib
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.ml.datasets.registry import get_dataset
from backend.app.ml.datasets.public_preprocessor import prepare_public_features
from backend.app.ml.split import split_dataset

DEFAULT_PUBLIC_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_fraud_dataset.csv", "creditcard.csv")
)

def train_public_benchmark(
    artifacts_dir: Optional[str] = None,
    csv_path: Optional[str] = None,
    target_column: str = "Class",
    version: str = "v1.0.0",
    seed: int = 42
) -> Dict[str, Any]:
    """
    Step 15: Public Benchmark Model Training.
    
    Guarantees:
    - Loads public dataset via Dataset Registry (get_dataset(source='public', ...)).
    - Uses PublicPreprocessor (prepare_public_features) preserving native V1..V28, Amount features.
    - 70% Train, 15% Validation, 15% Test split.
    - Preprocessing StandardScaler fitted ONLY on X_train.
    - XGBoost classifier fitted ONLY on X_train / y_train.
    - Artifacts stored separately under artifacts/public/v1.0.0/.
    - Does NOT overwrite synthetic artifacts under artifacts/v1.0.0/.
    - Does NOT calibrate probabilities or evaluate final test metrics yet.
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
    os.makedirs(version_dir, exist_ok=True)
    os.makedirs(public_artifacts_dir, exist_ok=True)

    # Task 1: Load public dataset via registry
    dataset_res = get_dataset(
        source="public",
        csv_path=effective_path,
        target_column=effective_target
    )

    # Task 2: Feature preparation via public preprocessor
    prep_data = prepare_public_features(dataset_res)
    df = prep_data.X.copy()
    df[effective_target] = prep_data.y.values
    feature_names = prep_data.feature_columns

    # Task 3: Data splitting (70% Train, 15% Val, 15% Test stratified)
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

    # Task 4: Preprocessing (StandardScaler fitted on X_train ONLY)
    preprocessor = StandardScaler()
    preprocessor.fit(X_train)

    X_train_scaled = preprocessor.transform(X_train)
    X_val_scaled = preprocessor.transform(X_val)
    X_test_scaled = preprocessor.transform(X_test)

    # Task 5: Public XGBoost Model (fitted on X_train ONLY)
    pos_count = int(y_train.sum())
    neg_count = int(len(y_train) - pos_count)
    scale_pos_weight = float(neg_count / max(1, pos_count))

    model_config = {
        "n_estimators": 150,
        "max_depth": 5,
        "learning_rate": 0.06,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "scale_pos_weight": scale_pos_weight,
        "random_state": seed,
        "eval_metric": "logloss"
    }

    model = xgb.XGBClassifier(**model_config)
    model.fit(X_train_scaled, y_train)

    # Raw probabilities for validation and test sets (uncalibrated)
    raw_val_probs = model.predict_proba(X_val_scaled)[:, 1]
    raw_test_probs = model.predict_proba(X_test_scaled)[:, 1]

    # Task 6 & 7: Save public model artifacts and metadata separately
    joblib.dump(model, os.path.join(version_dir, "model.joblib"))
    joblib.dump(model, os.path.join(public_artifacts_dir, "model.joblib"))

    joblib.dump(preprocessor, os.path.join(version_dir, "preprocessor.joblib"))
    joblib.dump(preprocessor, os.path.join(public_artifacts_dir, "preprocessor.joblib"))

    np.save(os.path.join(version_dir, "raw_val_probs.npy"), raw_val_probs)
    np.save(os.path.join(version_dir, "raw_test_probs.npy"), raw_test_probs)
    np.save(os.path.join(version_dir, "y_val.npy"), y_val.values)
    np.save(os.path.join(version_dir, "y_test.npy"), y_test.values)

    metadata = {
        "model_version": version,
        "dataset_source": "public",
        "dataset_type": "Public benchmark — locally supplied dataset",
        "dataset_path": effective_path,
        "dataset_size": dataset_res.sample_count,
        "fraud_count": dataset_res.fraud_count,
        "fraud_rate": round(dataset_res.fraud_rate, 4),
        "feature_columns": feature_names,
        "target_column": effective_target,
        "train_size": len(X_train),
        "validation_size": len(X_val),
        "test_size": len(X_test),
        "random_seed": seed,
        "model_configuration": {
            "n_estimators": 150,
            "max_depth": 5,
            "learning_rate": 0.06,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "scale_pos_weight": round(scale_pos_weight, 4),
            "random_state": seed,
            "eval_metric": "logloss"
        },
        "trained_at": datetime.now(timezone.utc).isoformat()
    }

    with open(os.path.join(version_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    with open(os.path.join(public_artifacts_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Public ML Pipeline SUCCESS] Public model package saved to: {version_dir}")
    return metadata

if __name__ == "__main__":
    train_public_benchmark()
