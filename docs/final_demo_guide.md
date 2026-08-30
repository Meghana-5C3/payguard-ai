# PayGuard AI - Final Presentation & Demonstration Guide

**Document Status**: Official Release & Presentation Guide  
**Model Version**: `v1.0.0`  
**System Status**: Production Ready (Dual-Pipeline Architecture)  

---

## 1. Before Starting

- Ensure Python 3.10+ and Node.js 18+ are installed.
- Ensure all Python dependencies (`fastapi`, `xgboost`, `scikit-learn`, `shap`, `joblib`, `pandas`) are installed.
- Ensure frontend dependencies (`react`, `typescript`, `vite`, `tailwindcss`, `axios`, `lucide-react`) are installed (`npm install` inside `frontend/`).
- Do **NOT** hardcode API keys or secrets in configuration files.

---

## 2. Start Backend Server Manually

> [!NOTE]
> **Run manually when ready**:
> ```bash
> uvicorn backend.app.main:app --reload --port 8000
> ```
> Backend API Swagger docs will be accessible at: `http://localhost:8000/docs`

---

## 3. Start Frontend UI Manually

> [!NOTE]
> **Run manually when ready**:
> ```bash
> cd frontend
> npm run dev
> ```
> Frontend User Interface will be accessible at: `http://localhost:5173`

---

## 4. Demonstrate Synthetic PayGuard Demo

1. Open Web Browser at `http://localhost:5173`.
2. Click on the **Risk Simulator** tab.
3. Select a preset user profile (e.g. *Alex Rivera* or *Devon Vance*) and merchant.
4. Click **Evaluate Transaction Risk (POST /api/risk/evaluate)**.
5. Highlight:
   - Dynamic Risk Score (0–1000) & Risk Level Badge.
   - Raw XGBoost Probability vs Isotonic Calibrated Probability.
   - Dynamic Policy Escalation (OTP Challenge or Analyst Queue).
   - Interactive SHAP Waterfall Chart (12 domain risk features).

---

## 5. Demonstrate Public Fraud Benchmark

1. Click on the **Public Benchmark** tab (`Database` icon).
2. Point out the **Research Disclaimer Panel**:
   > *"The public benchmark pipeline is intended for research, reproducibility, benchmarking, and demonstration. Its benchmark performance does not imply production payment-fraud detection capability."*
3. Point out the **PCA Feature Limitation Warning**:
   > *"Features V1 through V28 are PCA-transformed numerical components and do not directly correspond to business concepts such as device risk, IP reputation, transaction velocity, OTP failures, or merchant risk."*
4. Point out the **Frozen Benchmark Metrics Panel**:
   - **PR-AUC**: **`0.7842`** (Primary benchmark metric)
   - **ROC-AUC**: **`0.9586`**
   - **Precision**: **`0.9423`**
   - **Recall**: **`0.6622`**
   - **F1 Score**: **`0.7778`**
5. Click **Load Fraud Sample** preset button (auto-fills high-risk PCA features `V4=3.9979`, `V14=-4.2892`, `V12=-2.8999`).
6. Click **Analyze Public Transaction (POST /api/public/predict)**.
7. Observe prediction result:
   - Decision: **`FRAUD`** (Red)
   - Calibrated Probability: `99.99%`
   - Threshold: `0.5` (`fixed_default_0.5`)
   - Local SHAP attributions table with neutral PCA labels (`PCA-transformed component`).

---

## 6. Demonstrate Local SHAP Explainability

- Show local SHAP attributions returned under **Top Risk Drivers**.
- Highlight that `V14` and `V4` have the strongest marginal positive impact pushing the prediction toward `FRAUD`.
- Explain that SHAP values describe mathematical logit feature contribution and do not establish real-world causality.

---

## 7. Explain Architecture & Pipeline Separation

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
```

---

## 8. Important Presentation Questions & Answers (Q&A)

### Q1: What dataset did you use for the public benchmark?
> **Answer**: We used the Kaggle Credit Card Fraud Detection dataset (`creditcard.csv`, N=284,807 transactions with 492 fraud cases, 0.1727% fraud prevalence).

### Q2: What are V1 through V28?
> **Answer**: `V1` through `V28` are anonymized numerical features resulting from a Principal Component Analysis (PCA) transformation performed by the original data providers to protect confidentiality. They are abstract mathematical components and do not map to domain concepts like IP reputation or device age.

### Q3: Why did you use Isotonic Calibration?
> **Answer**: Highly imbalanced XGBoost models often output distorted uncalibrated probabilities. Applying Isotonic Regression on validation set predictions (`X_val`/`y_val` ONLY) reduced Expected Calibration Error (ECE) from 0.0037 down to 0.0001, providing well-calibrated probabilities for risk decisions.

### Q4: Why is the decision threshold set to 0.5?
> **Answer**: Threshold `0.5` is the frozen default decision boundary (`fixed_default_0.5`). To prevent target leakage and data snooping, threshold tuning on test set labels was strictly prohibited.

### Q5: Did you use the test set for training or calibration?
> **Answer**: No. Training was performed strictly on `X_train` (70%), calibration strictly on `X_val` (15%), and final held-out evaluation was conducted ONCE on `X_test` (15%).

### Q6: Can SHAP prove why a transaction is fraudulent?
> **Answer**: SHAP explains how specific feature values nudge the model output probability relative to a baseline training set sample. It measures model contribution, not real-world causality.

### Q7: Is this production-ready payment fraud detection?
> **Answer**: The public benchmark model is intended for research, benchmarking, and demonstration. Production deployment requires real-time feature engineering pipelines, proprietary risk signals, and continuous monitoring.

### Q8: Why are there two separate pipelines?
> **Answer**: To maintain strict architectural isolation. The Synthetic PayGuard pipeline demonstrates end-to-end domain risk scoring with human-in-the-loop policies, while the Public Benchmark pipeline reproduces Kaggle dataset benchmarks without cross-contamination.

### Q9: Why is the public model frozen?
> **Answer**: Freezing model weights, preprocessors, and calibrators guarantees reproducibility, prevents in-flight data corruption, and ensures real-time API endpoints perform inference ONLY (`model.fit()` is never called during API execution).
