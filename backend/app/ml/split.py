from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def split_dataset(
    df: pd.DataFrame,
    feature_names: List[str],
    target_name: str = "is_fraud",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
    stratify: bool = True,
    timestamp_column: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Refactored strict dataset splitting module supporting 70% Train, 15% Validation, 15% Test.
    Supports both stratified splitting and chronological splitting when timestamp_column is provided.
    
    Guarantees:
    1. No row index exists in more than one split.
    2. Total rows across splits equal source dataset count.
    3. Feature columns match exactly across all 3 splits.
    4. Target is strictly separated from features.
    5. Test data remains untouched as isolated DataFrames/Series copies.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Ratios must sum to 1.0"
    assert target_name in df.columns, f"Target column '{target_name}' missing from DataFrame"
    assert target_name not in feature_names, f"Target column '{target_name}' cannot be in feature_names"
    for feat in feature_names:
        assert feat in df.columns, f"Feature column '{feat}' missing from DataFrame"

    X = df[feature_names].copy()
    y = df[target_name].copy()

    if timestamp_column and timestamp_column in df.columns:
        # Chronological Splitting
        sorted_df = df.sort_values(by=timestamp_column).reset_index(drop=True)
        X_sorted = sorted_df[feature_names].copy()
        y_sorted = sorted_df[target_name].copy()

        n_total = len(sorted_df)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)

        X_train = X_sorted.iloc[:n_train].copy()
        y_train = y_sorted.iloc[:n_train].copy()

        X_val = X_sorted.iloc[n_train:n_train + n_val].copy()
        y_val = y_sorted.iloc[n_train:n_train + n_val].copy()

        X_test = X_sorted.iloc[n_train + n_val:].copy()
        y_test = y_sorted.iloc[n_train + n_val:].copy()

    else:
        # Stratified / Random Splitting
        stratify_y = y if stratify else None
        test_val_ratio = val_ratio + test_ratio  # 0.30 for 70/15/15

        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=test_val_ratio,
            random_state=seed,
            stratify=stratify_y
        )

        val_relative_ratio = val_ratio / test_val_ratio  # 0.50 for equal val/test split
        stratify_temp = y_temp if stratify else None

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=1.0 - val_relative_ratio,
            random_state=seed,
            stratify=stratify_temp
        )

    # STRICT ASSERTIONS
    train_idx = set(X_train.index)
    val_idx = set(X_val.index)
    test_idx = set(X_test.index)

    # Assertion 1: No row exists in more than one split
    assert len(train_idx & val_idx) == 0, "Index overlap detected between Train and Validation splits!"
    assert len(train_idx & test_idx) == 0, "Index overlap detected between Train and Test splits!"
    assert len(val_idx & test_idx) == 0, "Index overlap detected between Validation and Test splits!"

    # Assertion 2: Total sample count
    assert len(X_train) + len(X_val) + len(X_test) == len(df), "Total split sizes do not match source DataFrame count!"

    # Assertion 3: Feature columns are identical across splits
    assert list(X_train.columns) == list(feature_names), "X_train feature columns do not match feature_names"
    assert list(X_val.columns) == list(feature_names), "X_val feature columns do not match feature_names"
    assert list(X_test.columns) == list(feature_names), "X_test feature columns do not match feature_names"

    # Assertion 4: Target is separated
    assert target_name not in X_train.columns, f"Target '{target_name}' present in X_train columns"
    assert target_name not in X_val.columns, f"Target '{target_name}' present in X_val columns"
    assert target_name not in X_test.columns, f"Target '{target_name}' present in X_test columns"

    # Assertion 5: Test data remains untouched (deep copies returned)
    return X_train.copy(), X_val.copy(), X_test.copy(), y_train.copy(), y_val.copy(), y_test.copy()
