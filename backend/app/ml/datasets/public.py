import os
from typing import List, Optional
import pandas as pd
import numpy as np
from backend.app.ml.datasets.base import DatasetResult

def load_public_csv(path: str, target_column: str = "Class") -> DatasetResult:
    """
    Loads and validates a local public fraud dataset CSV file.
    
    Requirements:
    - Path must exist on local filesystem.
    - Target column must exist in CSV and contain binary (0/1) values.
    - Does NOT download data or modify column names.
    - Dynamically reports sample count, fraud count, fraud rate, and missing values.
    """
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Public dataset CSV file not found at path: '{path}'. Please provide a valid local CSV path.")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file at '{path}': {str(e)}")

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in CSV. Available columns: {list(df.columns)}")

    # Check target binary validity
    unique_vals = set(df[target_column].dropna().unique())
    if not unique_vals.issubset({0, 1, 0.0, 1.0}):
        raise ValueError(f"Target column '{target_column}' must be binary (containing only 0 and 1). Found unique values: {unique_vals}")

    feature_columns = [col for col in df.columns if col != target_column]
    
    sample_count = len(df)
    fraud_count = int((df[target_column] == 1).sum())
    fraud_rate = float(df[target_column].mean()) if sample_count > 0 else 0.0
    missing_value_count = int(df.isna().sum().sum())

    return DatasetResult(
        dataframe=df,
        feature_columns=feature_columns,
        target_column=target_column,
        dataset_source="public",
        dataset_type="Public benchmark — locally supplied dataset",
        sample_count=sample_count,
        fraud_count=fraud_count,
        fraud_rate=fraud_rate,
        missing_value_count=missing_value_count
    )
