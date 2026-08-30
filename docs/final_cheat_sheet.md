# PayGuard AI - Quick Reference Cheat Sheet

**PROJECT NAME**: PayGuard AI: Explainable & Adaptive Transaction Risk Manager  
**MODEL VERSION**: `v1.0.0`  
**DATASET**: Kaggle Credit Card Fraud Detection dataset (`creditcard.csv`, N=284,807, 492 fraud cases, 0.1727% fraud prevalence)  

---

### CORE METRICS & PARAMETERS

- **TOTAL FEATURES**: `30` (`Time` + `V1`..`V28` + `Amount`)
- **PCA FEATURES**: `V1` through `V28` (Anonymized numerical components; **NOT** assigned business labels)
- **ALGORITHM**: XGBoost (`xgb.XGBClassifier`, `scale_pos_weight=577.868`, `n_estimators=150`, `max_depth=5`)
- **CALIBRATION**: Isotonic Regression (Fitted on validation set `X_val`/`y_val` ONLY)
- **THRESHOLD**: `0.5` (`threshold_source: "fixed_default_0.5"`)
- **EXPLAINABILITY**: SHAP TreeExplainer (`shap.TreeExplainer` on training baseline samples)

---

### HELD-OUT TEST PERFORMANCE METRICS (N=42,722)

- **PR-AUC**: **`0.7842`** (Primary benchmark metric for highly imbalanced fraud)
- **ROC-AUC**: **`0.9586`**
- **PRECISION**: **`0.9423`**
- **RECALL**: **`0.6622`**
- **F1 SCORE**: **`0.7778`**
- **BRIER SCORE**: **`0.0005`** (Calibrated)
- **ECE**: **`0.0002`** (Calibrated)

---

### API ENDPOINTS & ARCHITECTURE SEPARATION

- **SYNTHETIC DEMO ENDPOINT**: `POST /api/risk/evaluate` (`artifacts/v1.0.0/`, 12 domain risk features + policy engine)
- **PUBLIC BENCHMARK ENDPOINT**: `POST /api/public/predict` (`artifacts/public/v1.0.0/`, 30 PCA features)

---

### CRITICAL RULES & DISCLAIMERS

> **SHAP Disclaimer**: SHAP values indicate mathematical logit model contribution and do not establish physical causality.

> **Research Disclaimer**: The public benchmark pipeline is intended for research, reproducibility, benchmarking, and demonstration. Its benchmark performance does not imply production payment-fraud detection capability.

> **PCA Warning**: V1-V28 are PCA-transformed numerical components and do not directly correspond to business concepts such as device risk, IP reputation, transaction velocity, OTP failures, or merchant risk.
