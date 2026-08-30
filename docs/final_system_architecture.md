# PayGuard AI - Final System Architecture Specification

**Document Version**: 1.0.0  
**Status**: Frozen Production Specification  
**Architecture Date**: August 27, 2026  

---

## 1. High-Level System Architecture

PayGuard AI is an enterprise-grade Explainable Adaptive Transaction Risk Manager built with dual independent ML execution pipelines:

```
                                  +---------------------------------------+
                                  |         React Frontend (Vite)         |
                                  +---------------------------------------+
                                                      |
                    +---------------------------------+---------------------------------+
                    |                                                                   |
          Synthetic Demo Tab                                                Public Benchmark Tab
                    |                                                                   |
         POST /api/risk/evaluate                                           POST /api/public/predict
                    |                                                                   |
  +-----------------------------------+                             +-----------------------------------+
  |   Synthetic Risk Engine Pipeline  |                             |  Public Benchmark XGBoost Pipeline|
  +-----------------------------------+                             +-----------------------------------+
  | - 12 Domain Risk Features         |                             | - 30 Native PCA Features          |
  | - XGBoost (v1.0.0)                |                             | - XGBoost (v1.0.0)                |
  | - Isotonic Calibrator             |                             | - Isotonic Calibrator             |
  | - Dynamic Policy Engine           |                             | - Fixed Threshold = 0.5           |
  | - SHAP TreeExplainer Local        |                             | - SHAP TreeExplainer Local        |
  +-----------------------------------+                             +-----------------------------------+
                    |                                                                   |
  artifacts/v1.0.0/                                                artifacts/public/v1.0.0/
```

---

## 2. Synthetic PayGuard Pipeline

- **Endpoint**: `POST /api/risk/evaluate`
- **Features**: 12 domain risk features (`amount`, `tx_velocity_1h`, `tx_velocity_24h`, `is_new_device`, `is_cross_border`, `mcc_risk_tier`, `ip_reputation_score`, etc.).
- **Model**: `XGBClassifier` trained on 25,000 synthetic transaction records (`seed=42`).
- **Policy Integration**: Dynamic rule escalation engine (ALLOW, VERIFY / OTP Challenge, ESCALATE_TO_ANALYST).
- **Artifact Location**: `backend/app/ml/artifacts/v1.0.0/`

---

## 3. Public Benchmark Pipeline

- **Endpoint**: `POST /api/public/predict`
- **Features**: 30 native public benchmark features (`Time`, `V1`..`V28`, `Amount`).
- **Dataset**: Locally supplied Kaggle Credit Card Fraud Detection dataset (`creditcard.csv`, N=284,807).
- **Model**: Frozen `XGBClassifier` (`scale_pos_weight=577.868`, `n_estimators=150`, `max_depth=5`).
- **Calibration**: Isotonic Regression fitted on validation predictions (`X_val`/`y_val` ONLY).
- **Threshold**: Fixed threshold `0.5` (`threshold_source: "fixed_default_0.5"`).
- **Artifact Location**: `backend/app/ml/artifacts/public/v1.0.0/`

---

## 4. Dataset Separation

- **Synthetic Dataset**: Generated via `backend/app/ml/synthetic_data.py` (25,000 rows).
- **Public Benchmark Dataset**: `backend/data/public_fraud_dataset.csv/creditcard.csv` (284,807 rows).
- **Zero Collision**: Feature schemas, training data splits, preprocessors, and stored model binaries are 100% isolated under separate filesystem paths.

---

## 5. Training Flow

1. **Stratified Split**: 70% Train, 15% Validation, 15% Test (`seed=42`).
2. **Preprocessor Fitting**: `StandardScaler` fitted on `X_train` ONLY.
3. **Model Fitting**: `xgb.XGBClassifier` fitted on `X_train_scaled` and `y_train` ONLY.
4. **Zero Test Leakage**: `X_test` and `y_test` are strictly excluded from preprocessor, model training, and calibrator fitting.

---

## 6. Calibration Flow

1. Raw model probabilities generated for validation set (`X_val_scaled`).
2. `ProbabilityCalibrator` fits Isotonic Regression on `(val_raw_probs, y_val)`.
3. Validation Brier Score improved from `0.0013` to `0.0005`; ECE improved from `0.0037` to `0.0001`.
4. Calibrator saved as frozen binary `calibrator.joblib`.

---

## 7. Evaluation Flow

1. Pipeline evaluated **ONCE** on untouched test set (`X_test`, `y_test`, N=42,722).
2. Frozen Held-Out Metrics:
   - **PR-AUC**: **`0.7842`** (Primary benchmark metric)
   - **ROC-AUC**: **`0.9586`**
   - **Precision**: **`0.9423`**
   - **Recall**: **`0.6622`**
   - **F1 Score**: **`0.7778`**
   - **Brier Score**: **`0.0005`**
   - **ECE**: **`0.0002`**

---

## 8. SHAP Explainability Architecture

- **Explainer**: `shap.TreeExplainer` initialized on frozen XGBoost model.
- **Attribution Format**: Local mean SHAP values computed for input transaction features.
- **PCA Disclaimer**: Native feature names (`V1`..`V28`) labeled strictly as `"PCA-transformed component"`. Zero synthetic business concept mapping.
- **Non-Causality**: Documentation explicitly highlights that SHAP values measure logit model contribution and do not prove real-world causality.

---

## 9. Public Inference API Contract

- **HTTP Method**: `POST /api/public/predict`
- **Request Body**: JSON containing 30 numerical float fields (`Time`, `V1`..`V28`, `Amount`).
- **Response Body**:
  ```json
  {
    "model_version": "v1.0.0",
    "dataset_source": "public",
    "dataset_type": "Public benchmark — locally supplied dataset",
    "raw_probability": 0.9998,
    "calibrated_probability": 0.9999,
    "threshold": 0.5,
    "threshold_source": "fixed_default_0.5",
    "calibration_method": "isotonic",
    "decision": "FRAUD",
    "top_positive_features": [...],
    "top_negative_features": [...]
  }
  ```

---

## 10. Frontend Integration

- **React Page**: `frontend/src/pages/PublicBenchmarkPage.tsx`
- **Navbar Integration**: Dedicated **Public Benchmark** tab (`Database` icon).
- **Features**:
  - Held-out test performance banner.
  - Interactive parameter form for all 30 features with sample preset loader.
  - Visual decision badge (**`FRAUD`** vs **`LEGITIMATE`**).
  - Raw vs calibrated probability progress gauge.
  - Local SHAP risk attributions table with neutral PCA labels.
  - Research disclaimer alert.

---

## 11. Security Boundaries & Secrets Control

- Zero hardcoded API keys (`GEMINI_API_KEY`, etc.) or database credentials in frontend or repository code.
- Inference services operate locally without external network API dependencies.
- Error handling returns generic sanitized HTTP messages without exposing internal file paths or stack traces.

---

## 12. Data Leakage Controls

- **Strict Isolation**: `X_test` and `y_test` were evaluated ONCE post-training and are NEVER accessed during real-time API inference.
- **Zero Retraining**: Real-time inference endpoints perform prediction ONLY (`model.fit()`, `calibrator.fit()`, `preprocessor.fit()` are never called).

---

## 13. Frozen Artifact Integrity

All public benchmark artifacts under `backend/app/ml/artifacts/public/v1.0.0/` are frozen and verified:
- `model.joblib`
- `preprocessor.joblib`
- `calibrator.joblib`
- `model_metrics.json`
- `shap_importance.json`

---

## 14. Research & Benchmark Disclaimer

> [!IMPORTANT]
> The public benchmark pipeline is intended for research, reproducibility, benchmarking, and demonstration. Its benchmark performance does not imply production payment-fraud detection capability.
> 
> Features V1 through V28 are PCA-transformed numerical components and do not directly correspond to business concepts such as device risk, IP reputation, transaction velocity, OTP failures, or merchant risk.
