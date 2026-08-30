# Model Card: PayGuard AI — Public Fraud Benchmark

**Model Name**: PayGuard AI — Public Fraud Benchmark  
**Model Version**: v1.0.0  
**Artifact Path**: `backend/app/ml/artifacts/public/v1.0.0/`  
**Dataset**: Locally supplied Credit Card Fraud Detection dataset (`creditcard.csv`)  
**Target Column**: `Class` (0 = Legitimate, 1 = Fraud)  
**Task Type**: Binary Fraud Classification  

---

## 1. Feature Specifications

- **Native Public Features (30)**: `Time`, `V1`, `V2`, `V3`, `V4`, `V5`, `V6`, `V7`, `V8`, `V9`, `V10`, `V11`, `V12`, `V13`, `V14`, `V15`, `V16`, `V17`, `V18`, `V19`, `V20`, `V21`, `V22`, `V23`, `V24`, `V25`, `V26`, `V27`, `V28`, `Amount`.
- **Feature Format**: All features are numerical float64 values standardized via `StandardScaler` fitted on training data ONLY.

---

## 2. Model Architecture & Hyperparameters

- **Algorithm**: XGBoost Classifier (`xgb.XGBClassifier`)
- **Key Parameters**:
  - `n_estimators`: 150
  - `max_depth`: 5
  - `learning_rate`: 0.06
  - `subsample`: 0.85
  - `colsample_bytree`: 0.85
  - `scale_pos_weight`: 577.868
  - `random_state`: 42
  - `eval_metric`: `"logloss"`

---

## 3. Calibration & Threshold Policy

- **Probability Calibrator**: Isotonic Regression (Fitted on validation set `X_val`/`y_val` predictions ONLY).
- **Decision Threshold**: Frozen default threshold `0.5` (`threshold_source: "fixed_default_0.5"`).

---

## 4. Evaluation Performance (Held-Out Test Set, N=42,722)

- **PR-AUC**: **0.7842** (Primary evaluation metric)
- **ROC-AUC**: **0.9586**
- **Precision**: **0.9423**
- **Recall**: **0.6622**
- **F1 Score**: **0.7778**
- **Brier Score**: **0.0005**
- **ECE**: **0.0002**

---

## 5. Model Explainability & SHAP Audit

- **Explainability Method**: `shap.TreeExplainer`
- **Global Feature Ranking (Top 5)**: `V4` (mean abs SHAP: 0.9808), `V14` (0.3608), `V12` (0.2387), `V8` (0.1587), `V27` (0.1367).
- **Local Explanation Availability**: Local feature attributions exported to `shap_importance.json` for validation profiles.
- **PCA Interpretation Limitation**: Features `V1`..`V28` represent abstract principal components. They do not map to synthetic domain features (such as IP reputation or device fingerprinting).
- **Non-Causal**: SHAP values explain model output contributions and do not establish real-world causality.

---

## 6. Model Limitations & Ethical Considerations

> [!CAUTION]
> **Limitations & Disclaimer**:
> 1. **Extreme Class Imbalance**: Fraud accounts for only 0.1727% of transactions in this benchmark.
> 2. **Abstract Features**: Features `V1`..`V28` are anonymized PCA components. They cannot be directly interpreted as domain business rules.
> 3. **Non-Production Claim**: Benchmark performance on historical Kaggle data does not guarantee performance on live payment transactions.
> 4. **No Synthetic Interference**: Public benchmark model artifacts are isolated under `artifacts/public/` and do not replace or affect the synthetic demo pipeline.
