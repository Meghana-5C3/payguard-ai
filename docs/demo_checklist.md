# PayGuard AI - Hackathon Demo Checklist & Walkthrough

**Document Status**: Official Demo Guide  
**Model Version**: `v1.0.0`  

---

## 1. Application Startup Steps

1. **Backend Server Startup**:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
2. **Frontend UI Startup**:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open Web Browser at `http://localhost:5173`.

---

## 2. Synthetic PayGuard Demonstration

- Navigate to **Risk Simulator** tab.
- Select sample transactions (Standard User vs High Risk VIP).
- Click **Evaluate Transaction Risk (POST /api/risk/evaluate)**.
- Demonstrate:
  - Dynamic risk score (0-1000) & risk level badge.
  - Raw probability vs Isotonic calibrated probability.
  - Dynamic policy triggers (OTP Challenge / Analyst Escalation).
  - Natural language risk explanation.
  - Interactive SHAP waterfall chart (12 domain features).

---

## 3. Analyst Queue & Policy Engine Walkthrough

- Navigate to **Analyst Queue** tab:
  - Review escalated transactions.
  - Demonstrate analyst override decision (APPROVE / REJECT) with audit logging.
- Navigate to **Policy Engine** tab:
  - Review active risk escalation rules.
  - Modify policy thresholds dynamically.

---

## 4. Public Fraud Benchmark Demonstration

- Navigate to **Public Benchmark** tab (`Database` icon).
- Point out the **Research Disclaimer Panel** highlighting that features `V1`..`V28` are anonymized PCA components.
- Point out the **Frozen Benchmark Metrics Panel**:
  - PR-AUC: `0.7842`
  - ROC-AUC: `0.9586`
  - Precision: `0.9423`
  - Recall: `0.6622`
  - F1 Score: `0.7778`
- Click **Load Fraud Sample** preset button (fills high risk PCA values: `V4=3.9979`, `V14=-4.2892`, `V12=-2.8999`).
- Click **Analyze Public Transaction (POST /api/public/predict)**.
- Observe instant inference response:
  - Decision badge: **`FRAUD`** (Red)
  - Calibrated probability: `99.99%`
  - Threshold: `0.5` (`fixed_default_0.5`)
  - Local SHAP attributions table displaying `V14` and `V4` as primary risk drivers.
- Click **Load Legit Sample** preset button and re-analyze to observe **`LEGITIMATE`** decision.

---

## 5. Security & Architectural Highlights

- **Dual Pipeline Isolation**: Synthetic demo pipeline (`/api/risk/evaluate`) and Public benchmark pipeline (`/api/public/predict`) are completely separate.
- **Zero Test Leakage**: Preprocessor and model fitted strictly on `X_train`; Calibrator fitted strictly on `X_val`; Test set (`X_test`) evaluated ONCE.
- **Zero In-Flight Training**: Inference endpoints perform predictions ONLY (`model.fit()` is NEVER called at runtime).

---

## 6. Key Disclaimers to Mention During Presentation

> "The public benchmark pipeline is intended for research, reproducibility, benchmarking, and demonstration. Its benchmark performance does not imply production payment-fraud detection capability."
> 
> "Features V1 through V28 are PCA-transformed numerical components and do not directly correspond to business concepts such as device risk, IP reputation, transaction velocity, OTP failures, or merchant risk."
