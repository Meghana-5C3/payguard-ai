# PayGuard AI - 2-Minute Project Viva Presentation Speech

> **Instructions for Student**: Read or deliver this natural 2-minute speech to your project examination panel.

---

"Good morning, Respected Examiners. 

My project is **PayGuard AI: An Explainable & Adaptive Transaction Risk Manager**.

In financial payment networks, fraud detection faces three core challenges: extreme class imbalance (often less than 0.2% fraud prevalence), distorted uncalibrated risk probabilities, and black-box opacity where models cannot explain why a transaction was declined.

To solve this, **PayGuard AI** introduces a dual-pipeline architecture built with **XGBoost classification**, **Isotonic probability calibration**, and **SHAP TreeExplainer local attributions**.

We implemented two isolated pipelines:
First, a **Synthetic Risk Pipeline** that evaluates 12 domain risk features—such as transaction velocity, device age, and IP reputation—integrated with an adaptive business policy engine for automated OTP verification and analyst queue escalation.

Second, a **Public Fraud Benchmark Pipeline** trained on the Kaggle Credit Card Fraud Detection dataset of 284,807 transactions. To handle the 577-to-1 class imbalance without synthetic data corruption, we utilized class-weighted loss functions (`scale_pos_weight=577.868`).

To ensure probability reliability, we fitted **Isotonic Regression** strictly on validation predictions, reducing Expected Calibration Error from `0.0037` down to `0.0001`. On the untouched held-out test set of 42,722 transactions, our frozen model achieved a **PR-AUC of 0.7842**, **ROC-AUC of 0.9586**, and an **F1 score of 0.7778**.

For compliance and transparency, we integrated **SHAP TreeExplainer** to generate local feature attributions per transaction. On the public benchmark UI, anonymized features `V1` through `V28` are strictly identified as neutral PCA components to prevent false domain claims.

Our system is implemented with a **FastAPI backend** and a **React 18 TypeScript frontend**, supported by 83 automated unit tests verifying strict zero data leakage.

Thank you, and I am ready for your questions."
