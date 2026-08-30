# PayGuard AI - Public Model Explainability & SHAP Audit Report

**Document Version**: 1.0.0  
**Audit Date**: August 27, 2026  
**Pipeline Status**: Frozen & Verified  
**Model Package**: `backend/app/ml/artifacts/public/v1.0.0/`  

---

## 1. Overview & Explanation Methodology

To audit feature contributions in the frozen Public XGBoost Fraud Benchmark model, SHAP (SHapley Additive exPlanations) values were generated using `shap.TreeExplainer`.

- **Explainer Type**: `shap.TreeExplainer`
- **Background Baseline Sample**: 100 random training set samples (`X_train`, `seed=42`)
- **Analysis Sample Size**: 1,000 random training set samples (`X_train`, `seed=42`)
- **Feature Scope**: 30 native public features (`Time`, `V1`..`V28`, `Amount`)
- **Data Isolation Guarantee**: Test labels (`y_test`) and test features (`X_test`) were **NOT** used during SHAP value computation or explainer initialization.

---

## 2. Global Feature Importance (Top 10 Ranked by Mean Absolute SHAP)

| Rank | Feature | Mean Absolute SHAP | Min SHAP | Max SHAP | Semantic Category |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **V4** | **0.9808** | -1.6363 | +2.6941 | Abstract PCA Component |
| **2** | **V14** | **0.3608** | -0.6684 | +4.0452 | Abstract PCA Component |
| **3** | **V12** | **0.2387** | -0.7194 | +2.3047 | Abstract PCA Component |
| **4** | **V8** | **0.1587** | -0.5777 | +0.5201 | Abstract PCA Component |
| **5** | **V27** | **0.1367** | -0.5013 | +0.2097 | Abstract PCA Component |
| **6** | **Time** | **0.1305** | -0.3150 | +0.2994 | Relative Time Offset (sec) |
| **7** | **V18** | **0.1232** | -0.3694 | +0.2507 | Abstract PCA Component |
| **8** | **V3** | **0.1175** | -0.8126 | +1.1462 | Abstract PCA Component |
| **9** | **Amount** | **0.0978** | -0.1957 | +0.9220 | Transaction Amount ($) |
| **10** | **V15** | **0.0931** | -0.6464 | +0.3626 | Abstract PCA Component |

---

## 3. Local Explanation Methodology & Samples

Local feature attribution maps describe how individual feature values nudge the model output probability for specific transaction profiles.

### Sample A: High-Risk Profile (`predicted_probability: 0.9998`)
- **Primary Risk Drivers (Positive SHAP)**:
  - `V14` (Value: `-8.95`, SHAP: `+3.8505`) — Severe negative anomaly in PCA component V14 strongly drives high fraud risk score.
  - `V4` (Value: `+6.49`, SHAP: `+2.4708`) — Positive deviation in PCA component V4 pushes model output towards fraud threshold.
  - `V12` (Value: `-11.05`, SHAP: `+2.2481`) — Extreme negative value in V12 contributes positively to fraud probability.

### Sample B: Median Risk Profile (`predicted_probability: 0.0005`)
- **Primary Mitigating Drivers (Negative SHAP)**:
  - `V4` (Value: `-0.90`, SHAP: `-1.2669`) — Moderate negative V4 value strongly suppresses fraud probability.

---

## 4. PCA Feature Semantic Disclaimer

> [!WARNING]
> **PCA Semantic Boundaries & Non-Causality**:
> 1. **Abstract Features**: Features `V1` through `V28` are mathematical principal components resulting from dimensionality reduction on private transaction fields.
> 2. **No Business Labeling**: Do **NOT** assign domain meanings to PCA components (e.g. claiming `V14` represents IP reputation or `V4` represents device age).
> 3. **Non-Causal**: SHAP values measure marginal feature contributions to model logit outputs; they do not imply direct real-world causal relationships.
> 4. **Pipeline Isolation**: The Public Benchmark feature schema remains completely separate from PayGuard AI's 12 synthetic domain features.
