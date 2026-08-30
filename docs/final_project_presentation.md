# PayGuard AI - Final Technical Presentation

**Project Title**: PayGuard AI: Explainable & Adaptive Transaction Risk Manager  
**Model Version**: `v1.0.0`  
**Architecture Date**: August 27, 2026  

---

## 1. Problem Statement

Financial payment networks process millions of transactions daily where fraudulent activity accounts for a tiny fraction of total volume (e.g. 0.17% prevalence in standard benchmark data). Modern fraud detection systems face three critical technical challenges:

1. **Extreme Class Imbalance**: Traditional machine learning classifiers struggle when legitimate cases heavily outnumber fraud cases (e.g. 577 to 1 ratio).
2. **Probability Distortion**: Uncalibrated gradient boosted models often output overconfident, skewed risk probabilities, making automated threshold decisions unreliable.
3. **Black-Box Opacity**: Financial regulations (e.g., FCRA, GDPR) require transparent explanations for declined transactions, which standard complex ML models cannot naturally provide.

---

## 2. Motivation

Existing commercial anti-fraud solutions often rely on rigid rule-based filters that generate high false-positive rates, annoying legitimate customers while missing sophisticated multi-vector attacks. PayGuard AI bridges the gap between state-of-the-art tree-based machine learning and regulatory explainability by combining **XGBoost classification**, **Isotonic probability calibration**, **SHAP local attribution**, and an **Adaptive Policy Escalation Engine**.

---

## 3. Core Objectives

- Develop a dual-pipeline architecture isolating real-time synthetic domain risk evaluation from Kaggle public fraud benchmark evaluation.
- Handle extreme class imbalance without synthetic oversampling by utilizing class-weighted loss functions (`scale_pos_weight=577.868`).
- Calibrate risk probabilities to guarantee low Expected Calibration Error (ECE < 0.001) using validation data ONLY.
- Expose local SHAP feature explanations per transaction for compliance transparency.
- Provide a clean, real-time FastAPI + React dashboard with zero test set data leakage.

---

## 4. Proposed Solution

PayGuard AI introduces a production-ready dual-pipeline system:

- **Synthetic Risk Pipeline**: Evaluates 12 real-world payment risk signals (`amount`, `tx_velocity_1h`, `is_new_device`, `mcc_risk_tier`, etc.) combined with a dynamic policy engine for real-time customer OTP challenges and analyst escalation.
- **Public Fraud Benchmark Pipeline**: Serves frozen Kaggle `creditcard.csv` benchmarks over a separate `/api/public/predict` endpoint, evaluating 30 native numerical features (`Time`, `V1`..`V28`, `Amount`).

---

## 5. System Architecture & Dual-Pipeline Separation

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

## 6. Synthetic PayGuard Pipeline

- **Endpoint**: `POST /api/risk/evaluate`
- **Features**: 12 domain risk features (`amount`, `tx_velocity_1h`, `tx_velocity_24h`, `tx_amount_sum_24h`, `is_new_device`, `is_cross_border`, `time_since_last_tx_sec`, `distance_from_home_km`, `mcc_risk_tier`, `ip_reputation_score`, `failed_otp_attempts_24h`).
- **Policy Engine**: Evaluates active JSON business rules to trigger `ALLOW`, `VERIFY` (SMS OTP challenge), or `HOLD` (escalate to analyst review queue).

---

## 7. Public Benchmark Pipeline

- **Endpoint**: `POST /api/public/predict`
- **Features**: 30 native public benchmark features (`Time`, `V1`..`V28`, `Amount`).
- **Dataset**: Kaggle Credit Card Fraud Detection dataset (`creditcard.csv`, N=284,807).
- **Execution**: Preprocesses input via frozen `StandardScaler`, predicts raw probability with frozen XGBoost model, applies frozen Isotonic calibrator, and compares against fixed threshold `0.5`.

---

## 8. Dataset & Features Specification

- **Public Benchmark Dataset**: 284,807 credit card transactions.
- **Class Breakdown**: 284,315 Legitimate (99.8273%), 492 Fraud (0.1727%).
- **Feature Count**: 30 numeric input features.
- **Pre-processing**: `StandardScaler` fitted strictly on `X_train` (70% split, N=199,364).

---

## 9. V1-V28 PCA Features Explanation

> [!WARNING]
> **PCA Component Interpretation Limitation**:
> Features `V1` through `V28` are anonymized numerical features obtained via Principal Component Analysis (PCA) by the original Kaggle dataset authors to protect user privacy.
> 
> They represent abstract mathematical vectors and do **NOT** map directly to business domain concepts (such as IP reputation, device risk, or transaction velocity). Neutral labels (`PCA-transformed component`) are strictly enforced across the system.

---

## 10. XGBoost Classification Model

- **Algorithm**: `xgb.XGBClassifier`
- **Hyperparameters**:
  - `n_estimators`: 150
  - `max_depth`: 5
  - `learning_rate`: 0.06
  - `subsample`: 0.85
  - `colsample_bytree`: 0.85
  - `scale_pos_weight`: 577.868 (Handles 577:1 imbalance)
  - `eval_metric`: `"logloss"`
  - `random_state`: 42

---

## 11. Isotonic Probability Calibration

- **Method**: Isotonic Regression fitted strictly on validation set predictions (`X_val`/`y_val` ONLY, N=42,721).
- **Impact**:
  - Validation Brier Score: Improved from `0.0013` to `0.0005`.
  - Expected Calibration Error (ECE): Improved from `0.0037` to `0.0001`.

---

## 12. Decision Threshold Policy

- **Fixed Threshold**: `0.5` (`threshold_source: "fixed_default_0.5"`).
- **Policy Rationale**: To maintain strict experimental integrity and eliminate target leakage, threshold tuning on test labels was strictly prohibited.

---

## 13. SHAP Local Explainability

- **Explainer Type**: `shap.TreeExplainer` initialized on `X_train` baseline samples.
- **Global Rankings**: Top drivers identified as `V4` (mean abs SHAP: 0.9808), `V14` (0.3608), `V12` (0.2387), `V8` (0.1587), `V27` (0.1367).
- **Non-Causality**: SHAP values explain marginal model logit contributions and do not establish real-world causality.

---

## 14. API & Service Architecture

- **Framework**: FastAPI (Python 3.10+) with Pydantic V2 schema validation.
- **Inference Mode**: Prediction-only execution (`model.fit()` is NEVER called during HTTP requests).

---

## 15. Frontend Architecture

- **Framework**: React 18 + TypeScript + Vite + TailwindCSS + Lucide Icons.
- **Design System**: Dark slate theme with interactive probability gauges and risk badges.

---

## 16. Security & Confidentiality

- Zero hardcoded API keys (`GEMINI_API_KEY`, etc.) or database passwords in repository files.
- Internal filesystem paths and stack traces suppressed from production API error responses.

---

## 17. Data Leakage Prevention Controls

- **Strict Data Splitting**: 70% Train (199,364), 15% Validation (42,721), 15% Test (42,722).
- **Isolation Guarantee**: Preprocessor fitted on `X_train` ONLY; Calibrator fitted on `X_val` ONLY; Test set (`X_test`) evaluated ONCE post-training.

---

## 18. Held-Out Test Evaluation Metrics

Evaluated on untouched test set ($N=42,722$):
- **PR-AUC**: **`0.7842`** (Primary imbalanced evaluation metric)
- **ROC-AUC**: **`0.9586`**
- **Precision**: **`0.9423`**
- **Recall**: **`0.6622`**
- **F1 Score**: **`0.7778`**
- **Brier Score**: **`0.0005`**
- **ECE**: **`0.0002`**
- **Confusion Matrix**: TN=42,645, FP=3, FN=25, TP=49.

---

## 19. Limitations

> [!CAUTION]
> 1. **PCA Abstraction**: Public features `V1`..`V28` lack business domain semantics.
> 2. **Non-Production Claim**: Benchmark performance on historical Kaggle data does not guarantee production payment-fraud detection performance.

---

## 20. Future Scope

- Integration of graph neural networks (GNNs) for entity network fraud cluster detection.
- Implementation of real-time streaming feature stores (e.g., Feast) for microsecond velocity calculations.

---

## 21. Conclusion

PayGuard AI demonstrates a robust, calibrated, explainable, and leak-free machine learning architecture. By strictly separating synthetic domain risk modeling from public benchmark evaluation, the system provides transparent risk assessments verified through 83 unit/pipeline tests and a clean React user interface.
