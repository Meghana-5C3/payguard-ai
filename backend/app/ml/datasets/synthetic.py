from typing import Optional
from backend.app.ml.datasets.base import DatasetResult
from backend.app.ml.synthetic_data import generate_synthetic_dataset, FEATURE_NAMES

def load_synthetic_dataset(n_samples: int = 25000, seed: int = 42) -> DatasetResult:
    """
    Wraps the existing synthetic dataset generator and returns a standardized DatasetResult.
    """
    df = generate_synthetic_dataset(n_samples=n_samples, seed=seed)
    target_column = "is_fraud"
    
    sample_count = len(df)
    fraud_count = int(df[target_column].sum())
    fraud_rate = float(df[target_column].mean())
    missing_value_count = int(df.isna().sum().sum())

    return DatasetResult(
        dataframe=df,
        feature_columns=list(FEATURE_NAMES),
        target_column=target_column,
        dataset_source="synthetic",
        dataset_type="Synthetic benchmark — generated dataset",
        sample_count=sample_count,
        fraud_count=fraud_count,
        fraud_rate=fraud_rate,
        missing_value_count=missing_value_count
    )
