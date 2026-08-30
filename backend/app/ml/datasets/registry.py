import os
from typing import Optional
from backend.app.ml.datasets.base import DatasetResult
from backend.app.ml.datasets.synthetic import load_synthetic_dataset
from backend.app.ml.datasets.public import load_public_csv

def get_dataset(
    source: str = "synthetic",
    csv_path: Optional[str] = None,
    target_column: str = "Class",
    n_samples: int = 25000,
    seed: int = 42
) -> DatasetResult:
    """
    Registry function to retrieve dataset adapter results.
    
    Supported sources:
    - "synthetic": Uses the existing synthetic dataset generator.
    - "public": Requires an explicit local CSV file path and target column name.
    
    Default source is "synthetic" to preserve backward compatibility.
    """
    source_clean = source.lower().strip()

    if source_clean == "synthetic":
        return load_synthetic_dataset(n_samples=n_samples, seed=seed)
    elif source_clean == "public":
        if not csv_path:
            raise ValueError("Public dataset requires an explicit local CSV file path (csv_path).")
        if not os.path.exists(csv_path):
            raise ValueError(f"Public dataset file not found at path: '{csv_path}'. Please provide a valid local CSV path.")
        return load_public_csv(path=csv_path, target_column=target_column)
    else:
        raise ValueError(f"Unsupported dataset source: '{source}'. Supported sources: 'synthetic', 'public'.")
