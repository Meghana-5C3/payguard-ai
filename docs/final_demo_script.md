# PayGuard AI - 5-Minute Step-by-Step Demo Script

**Total Duration**: 5 Minutes  
**Target Audience**: Project Examination Panel / Hackathon Judges  

---

### [0:00 – 0:30] SECTION 1: PROJECT INTRODUCTION & OVERVIEW

**WHAT TO CLICK / SHOW**:
- Open the application at `http://localhost:5173`.
- Show the top Navigation Bar with the brand logo (**PAYGUARD AI v1.0**).

**WHAT TO SAY**:
> *"Good morning. This is PayGuard AI, an Explainable and Adaptive Transaction Risk Manager. Payment networks face extreme class imbalance, distorted probabilities, and black-box opacity. PayGuard AI solves this by combining XGBoost classification, Isotonic probability calibration, local SHAP attributions, and an adaptive policy engine across two isolated pipelines: Synthetic Risk Evaluation and Public Benchmark Evaluation."*

---

### [0:30 – 1:30] SECTION 2: SYNTHETIC PAYGUARD DEMONSTRATION

**WHAT TO CLICK / SHOW**:
- Click on **Risk Simulator** tab.
- Select profile *Alex Rivera* (Standard User).
- Click **Evaluate Transaction Risk (POST /api/risk/evaluate)**.
- Point to the dynamic risk gauge score, raw vs calibrated probability, and SHAP waterfall chart.

**WHAT TO SAY**:
> *"Here in the Risk Simulator, we evaluate 12 domain risk features—such as transaction velocity, device fingerprinting, and IP reputation. Notice how the uncalibrated raw probability is refined by Isotonic Calibration. Below, the interactive SHAP waterfall chart visualizes exact feature attributions driving this specific risk score."*

---

### [1:30 – 3:00] SECTION 3: PUBLIC BENCHMARK DEMONSTRATION

**WHAT TO CLICK / SHOW**:
- Click on **Public Benchmark** tab (`Database` icon).
- Point to the **Research Disclaimer Panel** and **PCA Limitation Warning**.
- Point to the **Frozen Benchmark Metrics Panel** (PR-AUC: `0.7842`, ROC-AUC: `0.9586`, F1: `0.7778`).
- Click **Load Fraud Sample** preset button.
- Click **Analyze Public Transaction (POST /api/public/predict)**.

**WHAT TO SAY**:
> *"Now we switch to the Public Fraud Benchmark pipeline, which operates on a separate endpoint `/api/public/predict`. This model was trained on 284,807 transactions from the Kaggle dataset. Features V1 through V28 are anonymized PCA components. As emphasized in our disclaimer panel, they represent abstract numerical vectors. By loading a fraud sample preset and analyzing it, the model outputs a calibrated fraud decision of 99.99% under threshold 0.5."*

---

### [3:00 – 4:00] SECTION 4: PREDICTION RESULT & PROBABILITIES

**WHAT TO CLICK / SHOW**:
- Point to the **FRAUD** decision badge (Red).
- Point to the raw vs calibrated probability progress bar (`99.98%` raw -> `99.99%` calibrated).
- Point to the threshold label (`0.5`, `fixed_default_0.5`).

**WHAT TO SAY**:
> *"Notice the classification decision badge and probability progress bar. The raw probability straight from XGBoost is calibrated using Isotonic Regression fitted strictly on validation data. The threshold is fixed at 0.5 to prevent target leakage and data snooping."*

---

### [4:00 – 4:40] SECTION 5: LOCAL SHAP EXPLANATION

**WHAT TO CLICK / SHOW**:
- Scroll down to the **Top Risk Drivers (SHAP Values)** card.
- Point to `V14` (`+3.8505`) and `V4` (`+2.4708`).
- Point to the SHAP disclaimer line.

**WHAT TO SAY**:
> *"Below the decision, local SHAP attributions reveal why the model classified this transaction as fraud. Here, components V14 and V4 contributed the highest marginal positive impact toward the fraud threshold. We strictly maintain neutral PCA labels and state that SHAP indicates logit model contribution rather than real-world causality."*

---

### [4:40 – 5:00] SECTION 6: METRICS, LIMITATIONS & CONCLUSION

**WHAT TO CLICK / SHOW**:
- Point back to the held-out test performance metrics.
- Conclude presentation.

**WHAT TO SAY**:
> *"On our untouched test set of 42,722 transactions, PayGuard AI achieved a PR-AUC of 0.7842 and ROC-AUC of 0.9586 with zero test set data leakage. PayGuard AI provides a transparent, calibrated, and scientifically rigorous foundation for explainable transaction risk management. Thank you."*
