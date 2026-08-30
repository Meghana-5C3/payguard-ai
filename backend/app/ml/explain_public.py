import os
import sys
import json
import joblib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
import shap

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.ml.datasets.registry import get_dataset
from backend.app.ml.datasets.public_preprocessor import prepare_public_features
from backend.app.ml.split import split_dataset

DEFAULT_PUBLIC_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_fraud_dataset.csv", "creditcard.csv")
)

def explain_public_benchmark(
    artifacts_dir: Optional[str] = None,
    csv_path: Optional[str] = None,
    target_column: str = "Class",
    version: str = "v1.0.0",
    seed: int = 42,
    background_size: int = 100,
    analysis_size: int = 1000
) -> Dict[str, Any]:
    """
    Step 18: Public Model Explainability & SHAP Audit.
    
    Guarantees:
    - Loads frozen public model & preprocessor from artifacts/public/v1.0.0/.
    - Reconstructs training feature sample (X_train ONLY) for SHAP background and analysis samples.
    - NEVER uses test labels (y_test) or test samples (X_test) for explanation fitting/sampling.
    - Computes global mean absolute SHAP feature importance across native features (Time, V1..V28, Amount).
    - Preserves native PCA feature names; does NOT inject synthetic feature names.
    - Saves artifact to backend/app/ml/artifacts/public/v1.0.0/shap_importance.json.
    - Leaves synthetic model artifacts and benchmark performance metrics 100% untouched.
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

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        raise FileNotFoundError(f"Frozen public pipeline components missing in '{version_dir}'.")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    # 2. Reconstruct training set sample for SHAP calculation (X_train ONLY)
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

    # Transform X_train
    X_train_scaled = pd.DataFrame(preprocessor.transform(X_train), columns=feature_names)

    # Background sample (for SHAP explainer baseline)
    actual_bg_size = min(background_size, len(X_train_scaled))
    background_sample = X_train_scaled.sample(n=actual_bg_size, random_state=seed)

    # Analysis sample (for computing global SHAP values)
    actual_analysis_size = min(analysis_size, len(X_train_scaled))
    analysis_sample = X_train_scaled.sample(n=actual_analysis_size, random_state=seed)

    # 3. Compute SHAP values using TreeExplainer
    print("[Public SHAP Audit] Computing SHAP TreeExplainer values on training sample...")
    explainer = shap.TreeExplainer(model, data=background_sample)
    shap_values = explainer.shap_values(analysis_sample)

    # Handle binary output format if 2D list/array returned by SHAP
    if isinstance(shap_values, list):
        shap_vals_matrix = shap_values[1]
    elif len(shap_values.shape) == 3:
        shap_vals_matrix = shap_values[:, :, 1]
    else:
        shap_vals_matrix = shap_values

    # 4. Calculate Global Feature Importance (mean absolute SHAP)
    mean_abs_shap = np.mean(np.abs(shap_vals_matrix), axis=0)
    mean_shap = np.mean(shap_vals_matrix, axis=0)
    min_shap = np.min(shap_vals_matrix, axis=0)
    max_shap = np.max(shap_vals_matrix, axis=0)

    importance_list = []
    for idx, col in enumerate(feature_names):
        importance_list.append({
            "feature": col,
            "mean_absolute_shap": float(mean_abs_shap[idx]),
            "mean_shap": float(mean_shap[idx]),
            "minimum_shap": float(min_shap[idx]),
            "maximum_shap": float(max_shap[idx])
        })

    # Sort descending by mean_absolute_shap
    importance_list.sort(key=lambda x: x["mean_absolute_shap"], reverse=True)
    for rank, item in enumerate(importance_list, start=1):
        item["rank"] = rank

    # 5. Local Explanations for selected training/validation examples
    local_examples = []
    val_scaled = pd.DataFrame(preprocessor.transform(X_val), columns=feature_names)

    # Pick 3 deterministic validation examples: high risk, medium risk, low risk
    val_probs = model.predict_proba(val_scaled)[:, 1]
    high_idx = int(np.argmax(val_probs))
    low_idx = int(np.argmin(val_probs))
    med_idx = int(np.argsort(val_probs)[len(val_probs) // 2])

    val_shap_values = explainer.shap_values(val_scaled.iloc[[high_idx, med_idx, low_idx]])
    if isinstance(val_shap_values, list):
        val_shap_matrix = val_shap_values[1]
    elif len(val_shap_values.shape) == 3:
        val_shap_matrix = val_shap_values[:, :, 1]
    else:
        val_shap_matrix = val_shap_values

    example_indices = [high_idx, med_idx, low_idx]
    example_labels = ["high_risk", "median_risk", "low_risk"]

    for i, idx in enumerate(example_indices):
        prob = float(val_probs[idx])
        row_shap = val_shap_matrix[i]
        row_vals = val_scaled.iloc[idx].to_dict()

        feat_shaps = [{"feature": f, "shap_value": float(row_shap[j]), "feature_value": float(row_vals[f])} for j, f in enumerate(feature_names)]
        top_pos = sorted([f for f in feat_shaps if f["shap_value"] > 0], key=lambda x: x["shap_value"], reverse=True)[:5]
        top_neg = sorted([f for f in feat_shaps if f["shap_value"] < 0], key=lambda x: x["shap_value"])[:5]

        local_examples.append({
            "sample_type": example_labels[i],
            "validation_sample_index": idx,
            "predicted_probability": round(prob, 4),
            "top_positive_features": top_pos,
            "top_negative_features": top_neg
        })

    # 6. Save SHAP importance artifact
    shap_artifact = {
        "model_version": version,
        "dataset_source": "public",
        "dataset_type": "Public benchmark — locally supplied dataset",
        "feature_columns": feature_names,
        "explanation_method": "SHAP TreeExplainer",
        "background_sample_size": actual_bg_size,
        "analysis_sample_size": actual_analysis_size,
        "global_feature_importance": importance_list,
        "local_explanations": local_examples,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    out_path_ver = os.path.join(version_dir, "shap_importance.json")
    out_path_pub = os.path.join(public_artifacts_dir, "shap_importance.json")

    with open(out_path_ver, "w") as f:
        json.dump(shap_artifact, f, indent=2)

    with open(out_path_pub, "w") as f:
        json.dump(shap_artifact, f, indent=2)

    print(f"[Public SHAP Audit SUCCESS] SHAP importance artifact saved to: {out_path_ver}")
    return shap_artifact

if __name__ == "__main__":
    explain_public_benchmark()
