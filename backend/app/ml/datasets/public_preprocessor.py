from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from backend.app.ml.datasets.base import DatasetResult

PROHIBITED_ID_COLUMNS = ["transaction_id", "user_id", "id", "uuid", "index", "account_id"]

@dataclass
class PublicPreprocessedData:
    X: pd.DataFrame
    y: pd.Series
    feature_columns: List[str]
    preprocessor_metadata: Dict[str, Any]

def prepare_public_features(dataset_result: DatasetResult) -> PublicPreprocessedData:
    """
    Prepares features for the public benchmark pipeline.
    
    Guarantees:
    - Preserves original public feature column names (e.g. V1..V28, Amount).
    - Excludes target column from feature matrix X.
    - Strips prohibited non-predictive identifier columns.
    - Validates that feature columns are numeric; raises ValueError on unhandled object/string columns.
    - Does NOT inject synthetic domain feature names or fit preprocessors on test splits.
    - Does NOT train models or download data.
    """
    if not isinstance(dataset_result, DatasetResult):
        raise ValueError("Input must be a valid DatasetResult instance.")

    df = dataset_result.dataframe.copy()
    target_column = dataset_result.target_column

    if not target_column or target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' is missing from public dataset DataFrame.")

    # Validate target is binary
    y_raw = df[target_column]
    unique_target_vals = set(y_raw.dropna().unique())
    if not unique_target_vals.issubset({0, 1, 0.0, 1.0}):
        raise ValueError(f"Target column '{target_column}' must be binary (containing only 0 and 1). Found unique values: {unique_target_vals}")

    y = y_raw.astype(int)

    # Filter out target and prohibited identifier columns
    feature_columns = []
    removed_prohibited = []

    for col in df.columns:
        if col == target_column:
            continue
        col_lower = col.lower().strip()
        if any(pat == col_lower or col_lower.endswith("_id") for pat in PROHIBITED_ID_COLUMNS):
            removed_prohibited.append(col)
        else:
            feature_columns.append(col)

    X = df[feature_columns].copy()

    # Check for unhandled object/categorical/string columns
    unsupported_object_cols = []
    for col in X.columns:
        if not pd.api.types.is_numeric_dtype(X[col]):
            unsupported_object_cols.append(col)

    if unsupported_object_cols:
        raise ValueError(
            f"Public preprocessor encountered unsupported non-numeric object/string columns: {unsupported_object_cols}. "
            "Public benchmark pipeline requires explicit numeric features or pre-encoding."
        )

    # Impute missing values in numeric features if present
    missing_imputed_count = int(X.isna().sum().sum())
    if missing_imputed_count > 0:
        for col in X.columns:
            if X[col].isna().sum() > 0:
                X[col] = X[col].fillna(X[col].median())

    metadata = {
        "dataset_source": dataset_result.dataset_source,
        "dataset_type": dataset_result.dataset_type,
        "target_column": target_column,
        "n_features": len(feature_columns),
        "n_samples": len(X),
        "prohibited_columns_removed": removed_prohibited,
        "missing_values_imputed": missing_imputed_count,
        "feature_names": feature_columns
    }

    return PublicPreprocessedData(
        X=X,
        y=y,
        feature_columns=feature_columns,
        preprocessor_metadata=metadata
    )
