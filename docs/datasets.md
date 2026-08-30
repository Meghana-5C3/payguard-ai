# PayGuard AI - Datasets & Feature Pipeline Documentation

**Document Status**: Production Specification  
**Last Updated**: August 27, 2026  

---

## 1. Overview & Dataset Separation

PayGuard AI maintains strict architectural separation between two pipeline paths:

1. **Synthetic Demo Pipeline** (`dataset_source: "synthetic"`, `dataset_type: "Synthetic benchmark — generated dataset"`):
   - **Feature Vector**: 12 domain risk features (`amount`, `tx_amount_zscore`, `tx_velocity_1h`, `tx_velocity_24h`, `tx_amount_sum_24h`, `is_new_device`, `is_cross_border`, `time_since_last_tx_sec`, `distance_from_home_km`, `mcc_risk_tier`, `ip_reputation_score`, `failed_otp_attempts_24h`).
   - **Label Generation**: Probabilistic Bernoulli sampling (`np.random.default_rng.binomial`).
   - **Status**: **ACTIVE**. Fully trained, calibrated, evaluated, and serving live backend API endpoints.

2. **Public Benchmark Pipeline** (`dataset_source: "public"`, `dataset_type: "Public benchmark — locally supplied dataset"`):
   - **Feature Preprocessor**: Managed by `PublicDatasetAdapter` (`public.py`) and `prepare_public_features` (`public_preprocessor.py`).
   - **Feature Schema**: Preserves native raw CSV feature names (e.g. `V1`..`V28`, `Amount`). Zero synthetic feature name mapping or injection.
   - **Status**: **NOT TRAINED**. No public benchmark model has been trained because no local public dataset CSV file is currently supplied in the workspace environment.

---

## 2. Public CSV Adapter & Preprocessor Requirements

- **No Automatic Downloads**: The application does NOT download external datasets over the network.
- **Local File Path**: The caller must explicitly supply the local CSV file path.
- **Target Column**: Target column name must be provided (e.g., `"Class"` or `"is_fraud"`).
- **Target Format**: The target column must be binary, containing only `0` (legitimate) and `1` (fraud).
- **Numeric Feature Validation**: Unhandled non-numeric object/string columns trigger an explicit error during feature preparation.

---

## 3. How to Provide a Local Public CSV & Prepare Features

```python
from backend.app.ml.datasets.registry import get_dataset
from backend.app.ml.datasets.public_preprocessor import prepare_public_features

# 1. Load dataset via adapter
dataset_result = get_dataset(
    source="public",
    csv_path="path/to/local/creditcard.csv",
    target_column="Class"
)

# 2. Prepare features (preserves original V1..V28, Amount column names)
prep_data = prepare_public_features(dataset_result)

print("Public Features:", prep_data.feature_columns)
print("X shape:", prep_data.X.shape)
print("y shape:", prep_data.y.shape)
```

---

## 4. Key Differences: Synthetic vs Public

| Property | Synthetic Demo Pipeline | Public Benchmark Pipeline |
| :--- | :--- | :--- |
| **Dataset Source String** | `"synthetic"` | `"public"` |
| **Dataset Type String** | `"Synthetic benchmark — generated dataset"` | `"Public benchmark — locally supplied dataset"` |
| **Feature Schema** | 12 Domain Features (`amount`, `tx_velocity_1h`, etc.) | Custom CSV columns (e.g. `V1`, `V2`, `Amount`) |
| **Target Column** | `"is_fraud"` | Configurable (e.g., `"Class"`) |
| **Training Status** | Trained & Evaluated (`v1.0.0`) | **UNTRAINED** (No local CSV supplied) |
