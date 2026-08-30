from dataclasses import dataclass
from typing import List
import pandas as pd

@dataclass
class DatasetResult:
    dataframe: pd.DataFrame
    feature_columns: List[str]
    target_column: str
    dataset_source: str       # "synthetic" or "public"
    dataset_type: str         # "Synthetic benchmark — generated dataset" or "Public benchmark — locally supplied dataset"
    sample_count: int
    fraud_count: int
    fraud_rate: float
    missing_value_count: int
