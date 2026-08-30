# PayGuard AI - Public Benchmark Evaluation Report

**Document Version**: 1.0.0  
**Evaluation Date**: August 27, 2026  
**Pipeline Status**: Frozen & Verified  
**Dataset Source**: Public Benchmark Dataset (`creditcard.csv`)  

---

## 1. Dataset & Characteristics

- **Dataset File**: `backend/data/public_fraud_dataset.csv/creditcard.csv`
- **Total Sample Count**: 284,807 transactions
- **Total Fraud Count**: 492 transactions
- **Total Fraud Prevalence**: 0.1727% (Severe Class Imbalance: ~1 fraud per 578 legitimate transactions)
- **Missing Values**: 0 missing values across all 31 columns.
- **Duplicate Rows**: 1,081 rows (0.38%, preserved in raw CSV).

---

## 2. Feature Definitions & PCA Disclaimer

> [!IMPORTANT]
> **PCA Feature Transformation Disclaimer**:
> Features `V1` through `V28` are numerical principal components resulting from a PCA transformation on sensitive financial records.
> **DO NOT** map `V1`..`V28` to synthetic domain concepts such as transaction velocity (`tx_velocity_1h`), device age (`is_new_device`), IP reputation (`ip_reputation_score`), cross-border behavior (`is_cross_border`), or OTP failures (`failed_otp_attempts_24h`).
> The Public Benchmark Pipeline evaluates `V1`..`V28` strictly under their native column names.

- **Numerical Features (30)**: `Time`, `V1`, `V2`, `V3`, `V4`, `V5`, `V6`, `V7`, `V8`, `V9`, `V10`, `V11`, `V12`, `V13`, `V14`, `V15`, `V16`, `V17`, `V18`, `V19`, `V20`, `V21`, `V22`, `V23`, `V24`, `V25`, `V26`, `V27`, `V28`, `Amount`.
- **Target Column**: `Class` (0 = Legitimate, 1 = Fraud).

---

## 3. Data Split Strategy

- **Stratified Split Ratios**: 70% Train / 15% Validation / 15% Test (`seed=42`)
  - **Train Set**: 199,364 samples (344 fraud cases)
  - **Validation Set**: 42,721 samples (74 fraud cases)
  - **Held-Out Test Set**: 42,722 samples (74 fraud cases)
- **Isolation Verification**: The held-out test set (`X_test`, `y_test`) was kept strictly untouched during model training, hyperparameter configuration, preprocessor fitting, and probability calibration selection.

---

## 4. Model Configuration & Calibration Policy

- **Model Type**: XGBoost Classifier (`xgb.XGBClassifier`)
  - `n_estimators`: 150
  - `max_depth`: 5
  - `learning_rate`: 0.06
  - `subsample`: 0.85
  - `colsample_bytree`: 0.85
  - `scale_pos_weight`: 577.868 (Computed from training labels ONLY)
  - `random_state`: 42
  - `eval_metric`: `"logloss"`
- **Calibration Layer**: `ProbabilityCalibrator` (Isotonic Regression selected on `X_val`/`y_val` ONLY).
- **Threshold Policy**: Frozen default threshold `0.5` (`threshold_source: "fixed_default_0.5"`).

---

## 5. Final Held-Out Test Performance Metrics

Every metric below was dynamically computed ONCE on the untouched held-out test set (`X_test`, `y_test`, N=42,722):

| Metric | Value | Primary Benchmark Interpretation |
| :--- | :--- | :--- |
| **PR-AUC** | **0.7842** | **Primary metric for highly imbalanced fraud detection** |
| **ROC-AUC** | **0.9586** | Global discrimination capacity |
| **Precision** | **0.9423** | Low false positive rate among flagged alerts |
| **Recall** | **0.6622** | Fraction of actual fraud cases caught at 0.5 threshold |
| **F1 Score** | **0.7778** | Harmonic mean of Precision and Recall |
| **Brier Score** | **0.0005** | Mean squared probability error (Calibrated) |
| **Expected Calibration Error (ECE)** | **0.0002** | Decile-level calibration error |

---

## 6. Confusion Matrix (Test Set, N=42,722, Threshold=0.5)

```
                       Predicted Legitimate (0)    Predicted Fraud (1)
Actual Legitimate (0)           42,645 (TN)                 3 (FP)
Actual Fraud (1)                    25 (FN)                49 (TP)
```

- **True Negatives (TN)**: 42,645
- **False Positives (FP)**: 3 (Extremely low false alarm rate: 0.007%)
- **False Negatives (FN)**: 25
- **True Positives (TP)**: 49

---

## 7. Calibration Improvement (Uncalibrated vs Calibrated Test Set)

| Metric | Raw / Uncalibrated | Calibrated (Isotonic) | Improvement |
| :--- | :--- | :--- | :--- |
| **Brier Loss** | 0.0011 | **0.0005** | **54.5% Reduction** |
| **Expected Calibration Error (ECE)** | 0.0036 | **0.0002** | **94.4% Reduction** |

---

## 8. Limitations & Pipeline Separation

1. **Synthetic vs Public Separation**: The Public Benchmark Pipeline runs on PCA features (`V1`..`V28`, `Amount`) and is isolated under `backend/app/ml/artifacts/public/`. It does not collide with or replace the Synthetic Demo Pipeline (`backend/app/ml/artifacts/v1.0.0/`).
2. **Benchmark Scope**: High PR-AUC on Kaggle `creditcard.csv` demonstrates benchmark model capability on historical anonymized data but does not imply real-time payment gateway performance on live domestic or international payment rails.
