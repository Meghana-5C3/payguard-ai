# PayGuard AI - Master Viva Questions & Detailed Technical Answers

**Document Version**: 1.0.0  
**Target**: B.Tech CSE Viva / Project Defense Examination  
**Project**: PayGuard AI: Explainable & Adaptive Transaction Risk Manager  

---

### Q1: What is PayGuard AI?
**Answer**: PayGuard AI is an enterprise-grade transaction risk evaluation system that combines XGBoost machine learning, Isotonic probability calibration, local SHAP explainability, and an adaptive policy escalation engine. It features two separate execution pipelines: a Synthetic Risk Engine for domain transactions and a Public Fraud Benchmark Pipeline for Kaggle credit card benchmarks.

### Q2: What problem does PayGuard AI solve?
**Answer**: It solves the problem of high false-positive rates, uncalibrated risk probabilities, and black-box opacity in automated payment fraud detection systems under extreme class imbalance.

### Q3: Why did you choose fraud detection as your project domain?
**Answer**: Fraud detection presents critical computer science challenges: severe class imbalance (0.17% fraud prevalence), high cost of false positives (lost customer trust), strict latency requirements, and mandatory explainability under financial regulations (GDPR, FCRA).

### Q4: What dataset does the public benchmark use?
**Answer**: The public benchmark uses the Kaggle Credit Card Fraud Detection dataset (`creditcard.csv`, N=284,807 transactions with 492 fraud cases, 0.1727% fraud prevalence).

### Q5: What are the 30 features expected by the public benchmark?
**Answer**: `Time` (relative elapsed seconds), `V1` through `V28` (PCA numerical components), and `Amount` (transaction dollar value).

### Q6: What are V1 through V28?
**Answer**: `V1` through `V28` are anonymized numerical features generated via Principal Component Analysis (PCA) by the dataset provider to protect user privacy.

### Q7: Why are V1-V28 PCA-transformed components?
**Answer**: To anonymize confidential cardholder transaction information (such as personal credentials and account details) before public release.

### Q8: Why should we not assign business meanings (like device risk or velocity) to V1-V28?
**Answer**: Assigning domain business meanings to PCA features is scientifically invalid. PCA features are linear orthogonal combinations of original private features; they do not correspond 1-to-1 with specific physical concepts like IP reputation or OTP failures.

### Q9: Why did you select XGBoost for classification?
**Answer**: XGBoost (eXtreme Gradient Boosting) handles tabular feature interactions effectively, natively supports instance weighting (`scale_pos_weight`) for class imbalance, and integrates cleanly with tree-based SHAP explainers.

### Q10: What is XGBoost?
**Answer**: XGBoost is an optimized distributed gradient boosting library that implements machine learning algorithms under the Gradient Boosting framework using decision trees.

### Q11: What is Isotonic Calibration?
**Answer**: Isotonic Regression is a non-parametric calibration method that fits a non-decreasing step function to map raw model logit probabilities to true empirical probabilities.

### Q12: Why is probability calibration required?
**Answer**: Gradient boosted models often output distorted uncalibrated probabilities due to tree depth optimization and class weighting. Calibration ensures that a predicted probability of 0.80 means approximately 80% of such transactions are actually fraudulent.

### Q13: What is the difference between raw probability and calibrated probability?
**Answer**: Raw probability is the uncalibrated output straight from XGBoost's sigmoid transformation. Calibrated probability is the probability refined by Isotonic Regression to accurately match empirical fraud rates.

### Q14: Why is the decision threshold set to 0.5?
**Answer**: Fixed threshold `0.5` (`threshold_source: "fixed_default_0.5"`) serves as the standard un-biased decision boundary.

### Q15: Why was threshold optimization not performed on the test set?
**Answer**: Optimizing the decision threshold using test set labels introduces target leakage and data snooping, resulting in overly optimistic benchmark metrics that fail in real-world deployments.

### Q16: What is ROC-AUC?
**Answer**: Receiver Operating Characteristic - Area Under the Curve measures the model's ability to discriminate between positive and negative classes across all possible thresholds (Plotting True Positive Rate vs False Positive Rate).

### Q17: What is PR-AUC?
**Answer**: Precision-Recall Area Under the Curve evaluates Precision vs Recall across all thresholds. It is much more informative than ROC-AUC for highly imbalanced datasets.

### Q18: Why is PR-AUC useful for highly imbalanced fraud detection?
**Answer**: In datasets where 99.83% of transactions are legitimate, a high ROC-AUC can be misleading because the False Positive Rate stays small even with thousands of false alarms. PR-AUC focuses directly on the minority positive fraud class.

### Q19: What is Precision?
**Answer**: Precision is $\frac{TP}{TP + FP}$, measuring the proportion of transactions flagged as fraud that are actually fraudulent (minimizing false alarms).

### Q20: What is Recall?
**Answer**: Recall is $\frac{TP}{TP + FN}$, measuring the proportion of actual fraud transactions correctly caught by the model.

### Q21: What is the F1 Score?
**Answer**: F1 Score is the harmonic mean of Precision and Recall ($\frac{2 \cdot P \cdot R}{P + R}$), providing a single balanced metric.

### Q22: What is SHAP?
**Answer**: SHAP (SHapley Additive exPlanations) is a game-theoretic approach to explain the output of any machine learning model by computing Shapley values representing each feature's marginal contribution.

### Q23: What is TreeExplainer?
**Answer**: `shap.TreeExplainer` is a fast algorithm designed specifically for decision tree ensembles (like XGBoost) to compute exact SHAP values in polynomial time.

### Q24: Does SHAP prove causality?
**Answer**: No. SHAP measures mathematical feature contributions to the model's output probability; it does not prove real-world physical causality.

### Q25: How did you prevent data leakage in your project?
**Answer**: We enforced strict 70/15/15 data splitting: `StandardScaler` was fitted strictly on `X_train`, `ProbabilityCalibrator` was fitted strictly on `X_val`, and `X_test`/`y_test` were evaluated ONCE post-training.

### Q26: What data was used for model training?
**Answer**: `X_train` and `y_train` ONLY (70% split, N=199,364).

### Q27: What data was used for calibration?
**Answer**: `X_val` predictions and `y_val` ONLY (15% split, N=42,721).

### Q28: What data was used for final evaluation?
**Answer**: `X_test` and `y_test` ONLY (15% split, N=42,722).

### Q29: Was the test set used for training or calibration?
**Answer**: Absolutely not. The test set remained completely untouched during feature scaling, model fitting, and calibrator tuning.

### Q30: Why are there two separate pipelines in PayGuard AI?
**Answer**: To separate synthetic domain risk evaluation (with 12 domain risk features and policy rules) from Kaggle public benchmark evaluation (30 PCA features) without cross-contamination.

### Q31: What is the difference between the synthetic and public pipelines?
**Answer**: The synthetic pipeline uses 12 domain risk features (`amount`, `tx_velocity`, `device_age`) over `/api/risk/evaluate`. The public pipeline uses 30 PCA features (`Time`, `V1`..`V28`, `Amount`) over `/api/public/predict`.

### Q32: What does `/api/risk/evaluate` do?
**Answer**: It evaluates synthetic payment transactions, computes domain risk features, passes them to XGBoost + Isotonic Calibrator, and applies dynamic policy escalation rules.

### Q33: What does `/api/public/predict` do?
**Answer**: It performs real-time inference on 30 public benchmark features using the frozen Kaggle-trained XGBoost model and Isotonic calibrator.

### Q34: How does the frontend communicate with the backend?
**Answer**: The React frontend sends asynchronous HTTP POST JSON requests via `axios` to FastAPI REST endpoints and renders real-time responses.

### Q35: What happens during real-time inference?
**Answer**: Input JSON is validated, scaled via frozen `StandardScaler.transform()`, evaluated via frozen `XGBoost.predict_proba()`, calibrated via frozen `ProbabilityCalibrator.predict()`, and classified against threshold `0.5`.

### Q36: Does inference retrain or modify the model?
**Answer**: No. Inference is strictly prediction-only (`model.fit()` and `calibrator.fit()` are NEVER called at runtime).

### Q37: How are invalid inputs handled?
**Answer**: Missing or non-numeric feature inputs trigger Pydantic V2 schema validation errors returning HTTP 400 Bad Request responses.

### Q38: How are secrets and private keys protected?
**Answer**: Zero hardcoded secrets, passwords, or API keys exist in frontend or repository code. Internal stack traces are suppressed from API outputs.

### Q39: Is this system production-ready for live payment processing?
**Answer**: PayGuard AI is a production-grade research and demonstration prototype. Live payment deployment requires real-time streaming feature stores and fraud pattern monitoring.

### Q40: What are the main limitations of the public benchmark model?
**Answer**: Features `V1`..`V28` are anonymized PCA components lacking domain business semantics, and historical benchmark performance does not guarantee live payment performance.

### Q41: What is the future scope of this project?
**Answer**: Adding Graph Neural Networks (GNNs) for syndicate fraud ring detection and real-time streaming velocity calculation via Apache Kafka.

### Q42: Why is the public model package frozen under `artifacts/public/v1.0.0/`?
**Answer**: To ensure reproducibility, prevent accidental model drift, and maintain strict separation between demo execution and offline training.

### Q43: Why should benchmark metrics remain frozen?
**Answer**: Metrics evaluate a frozen model snapshot on a fixed test set. Modifying metrics invalidates scientific benchmark comparability.

### Q44: What does `v1.0.0` mean?
**Answer**: Semantic versioning denoting the major release version of the trained model, preprocessor, and calibrator artifact package.

### Q45: Why was Isotonic calibration chosen over Platt Scaling?
**Answer**: On validation experiments, Isotonic Regression achieved lower Expected Calibration Error (ECE: 0.0001) compared to Platt Scaling (sigmoid) because it fits non-parametric step functions without assuming logistic distribution shapes.

### Q46: What does a SHAP value of +2.47 for feature V4 mean?
**Answer**: It means that the specific value of `V4` in this transaction increased the logit prediction output by 2.47 units relative to the baseline training set expectation.

### Q47: Can SHAP prove that a transaction is fraudulent?
**Answer**: No. SHAP explains feature contribution to the model's output probability; it does not prove physical real-world fraud causality.

### Q48: How is experiment reproducibility maintained?
**Answer**: By fixing pseudo-random seeds (`seed=42`) across dataset generation, data splitting, XGBoost initialization, and SHAP background sampling.

### Q49: What makes PayGuard AI secure?
**Answer**: Pydantic input validation, strict separation of public and synthetic endpoints, zero hardcoded secrets, and error log sanitization.

### Q50: What makes your held-out test evaluation trustworthy?
**Answer**: Strict zero data leakage: `X_test` and `y_test` were never used during feature scaling, class weight calculation, tree fitting, or calibrator selection.
