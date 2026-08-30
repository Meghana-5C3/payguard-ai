# PayGuard AI - Job Interview & Resume Explanation Guide

**Document Status**: Official Technical Interview Guide  
**Project**: PayGuard AI: Explainable & Adaptive Transaction Risk Manager  

---

## 1. 30-Second Elevator Pitch

> *"PayGuard AI is an explainable fraud detection engine that addresses extreme class imbalance and probability distortion in payment networks. It combines XGBoost classification with Isotonic probability calibration and SHAP local feature attributions, delivering a 0.7842 PR-AUC on benchmark credit card data with transparent explanations and zero data leakage."*

---

## 2. 1-Minute Technical Summary

> *"In payment networks, fraud cases represent less than 0.2% of transactions, leading to severely uncalibrated risk scores and high false positives. PayGuard AI implements a dual-pipeline architecture: a Synthetic Domain Pipeline for real-world risk policies and a Public Benchmark Pipeline trained on 284,807 Kaggle transactions. We handled 577-to-1 class imbalance using instance-weighted loss functions (`scale_pos_weight=577.868`), calibrated probabilities via Isotonic Regression to achieve an Expected Calibration Error below 0.0002, and integrated SHAP TreeExplainer for feature attribution transparency over FastAPI REST endpoints and a React dashboard."*

---

## 3. 2-Minute Deep Technical Explanation

> *"PayGuard AI was architected around three core computer science principles: probability calibration, explainable AI, and strict experimental isolation.*
> 
> *First, we addressed class imbalance by training an XGBoost classifier on 70% of the dataset with `scale_pos_weight=577.868`. Because raw boosting probabilities skew under class weighting, we fitted an Isotonic Regression calibrator on validation set predictions (`X_val`/`y_val` ONLY), reducing ECE from 0.0037 to 0.0001.*
> 
> *Second, for transparency, we integrated SHAP TreeExplainer to compute exact Shapley attributions for all 30 features (`Time`, `V1`..`V28`, `Amount`). To preserve scientific integrity, features V1 through V28 are strictly treated as anonymized PCA components without fictitious business labeling.*
> 
> *Third, we built two isolated execution pathways: `/api/risk/evaluate` for synthetic domain risk escalation and `/api/public/predict` for frozen public benchmark inference. On the untouched held-out test set of 42,722 transactions, the frozen model achieved PR-AUC=0.7842, ROC-AUC=0.9586, and F1=0.7778. The backend is implemented in FastAPI with 83 automated unit tests, connected to a React 18 TypeScript UI."*

---

## 4. Resume Bullet Points

- **Architected Dual-Pipeline ML System**: Built FastAPI backend and React 18 dashboard for real-time transaction risk scoring across synthetic domain rules and public fraud benchmarks.
- **Calibrated Imbalanced XGBoost Classifier**: Implemented Isotonic Regression calibration on validation set predictions, reducing Expected Calibration Error (ECE) from 0.0037 to 0.0001 while handling 577:1 class imbalance.
- **Implemented Explainable AI (XAI)**: Integrated `shap.TreeExplainer` for per-transaction Shapley feature attributions, delivering regulatory transparency with zero data leakage on held-out test data (PR-AUC: 0.7842, ROC-AUC: 0.9586).
- **Enforced Zero Data Leakage**: Designed 70/15/15 stratified data splitting and automated 83 unit/pipeline tests verifying preprocessor and calibrator state isolation.

---

## 5. Individual Technical Contribution Statement

[Describe your actual contribution here based on your assigned team responsibilities, e.g., ML Pipeline Architecture, Calibration & SHAP Integration, FastAPI REST API Development, or React Dashboard Design.]
