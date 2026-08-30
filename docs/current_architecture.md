# PayGuard AI - Current System Architecture

**Document Type**: Baseline System Architecture Inspection  
**Date**: August 26, 2026  
**Status**: Development Checkpoint (Phase 0)  

---

## 1. System Overview

PayGuard AI is an enterprise transaction risk management platform structured into four decoupled layers:

```
[ Frontend (React SPA) ]
       │  HTTP REST
       ▼
[ FastAPI Backend API ] ────► [ Feature Engine ] ────► [ XGBoost Model + Isotonic Calibrator ]
       │                             │                                 │
       ▼                             ▼                                 ▼
[ SQLite Database ] ◄──── [ Audit Logger ] ◄──── [ Adaptive Policy Engine ] ◄──── [ SHAP Explainer ]
```

---

## 2. Component Inspection & Mapping

### A. Backend Entry Point
- **File**: [`backend/app/main.py`](file:///d:/PayGuard%20AI/backend/app/main.py)
- **Role**: Initializes SQLite database schema (`Base.metadata.create_all`), seeds demo users and merchants on startup, configures CORS middleware, and mounts API routers.

### B. Machine Learning Pipeline & Training
- **File**: [`backend/app/ml/train.py`](file:///d:/PayGuard%20AI/backend/app/ml/train.py)
- **Dataset Generation**: `generate_synthetic_dataset(n_samples=25000, seed=42)` generates synthetic feature vectors and samples ground truth labels via stochastic Bernoulli sampling (`labels = np.random.binomial(n=1, p=proba)`).
- **Model**: `xgboost.XGBClassifier` (150 trees, max_depth=5, learning_rate=0.06).
- **Probability Calibration**: `sklearn.isotonic.IsotonicRegression` fitted on validation set (`X_val`, `y_val`) probabilities.
- **Explainability**: `shap.TreeExplainer` fitted on the XGBoost model.

### C. Preprocessing & Feature Engineering
- **File**: [`backend/app/services/feature_engine.py`](file:///d:/PayGuard%20AI/backend/app/services/feature_engine.py)
- **Functions**: `compute_transaction_features()` calculates 1-hour and 24-hour transaction velocity, 30-day user amount z-score, Haversine geolocation distance from home, device fingerprint familiarity, cross-border status, MCC risk tier, and IP reputation score.

### D. Model Artifact Location
- **Directory**: [`backend/app/ml/artifacts/`](file:///d:/PayGuard%20AI/backend/app/ml/artifacts/)
- **Artifacts**:
  - `model.joblib`: Serialized XGBoost model object.
  - `calibrator.joblib`: Serialized Isotonic Regression object.
  - `shap_explainer.joblib`: Serialized SHAP TreeExplainer object.
  - `background_sample.joblib`: 100-sample training background dataframe.
  - `metrics.json`: Un-hardcoded test evaluation results, calibration curves, PR curves, and dataset metadata.

### E. Risk Engine (Inference & Calibration)
- **File**: [`backend/app/services/inference_service.py`](file:///d:/PayGuard%20AI/backend/app/services/inference_service.py)
- **Role**: Loads joblib artifacts, evaluates raw XGBoost predictions on incoming `FeatureVector` payloads, applies Isotonic calibration, and converts calibrated probabilities to a 0–1000 Risk Score.

### F. Adaptive Policy Engine
- **File**: [`backend/app/services/policy_engine.py`](file:///d:/PayGuard%20AI/backend/app/services/policy_engine.py)
- **Role**: Loads active `PolicyRule` records from SQLite and evaluates conditional logic over features and risk scores to assign authoritative actions (`APPROVE`, `VERIFY`, `HOLD`).

### G. SHAP Explainability Service
- **File**: [`backend/app/services/shap_service.py`](file:///d:/PayGuard%20AI/backend/app/services/shap_service.py)
- **Role**: Evaluates TreeExplainer attributions in <15ms for a feature vector, extracts top positive/negative risk drivers, and formats natural language explanation text.

### H. Persistence & Database Models
- **Database File**: [`backend/payguard.db`](file:///d:/PayGuard%20AI/backend/payguard.db) (SQLite)
- **Models File**: [`backend/app/models.py`](file:///d:/PayGuard%20AI/backend/app/models.py)
- **Tables**: `users`, `merchants`, `transactions`, `feature_vectors`, `risk_evaluations`, `policy_rules`, `audit_logs`.

### I. API Routes
- [`backend/app/api/risk.py`](file:///d:/PayGuard%20AI/backend/app/api/risk.py): `POST /api/v1/risk/evaluate`, `POST /api/v1/risk/verify`
- [`backend/app/api/analyst.py`](file:///d:/PayGuard%20AI/backend/app/api/analyst.py): `GET /api/v1/analyst/queue`, `POST /api/v1/analyst/override`
- [`backend/app/api/policies.py`](file:///d:/PayGuard%20AI/backend/app/api/policies.py): `GET /api/v1/policies`, `POST /api/v1/policies`, `PUT /api/v1/policies/{id}`, `POST /api/v1/policies/reset-defaults`
- [`backend/app/api/metrics.py`](file:///d:/PayGuard%20AI/backend/app/api/metrics.py): `GET /api/v1/metrics/performance`
- [`backend/app/api/audit.py`](file:///d:/PayGuard%20AI/backend/app/api/audit.py): `GET /api/v1/audit/logs`

### J. Frontend Pages & Components
- **Location**: [`frontend/src/`](file:///d:/PayGuard%20AI/frontend/src/)
- **Pages**:
  - `pages/SimulatorPage.tsx`: Live risk evaluation simulator & 2FA challenge modal.
  - `pages/AnalystPage.tsx`: Fraud analyst queue & human decision override drawer.
  - `pages/PolicyPage.tsx`: Adaptive risk policy matrix manager.
  - `pages/MetricsPage.tsx`: Reliability calibration diagrams, PR curves, and audit log table.
- **Components**: `Navbar.tsx`, `RiskGauge.tsx`, `ShapWaterfall.tsx`, `OtpModal.tsx`.

### K. Test Suite
- [`backend/tests/run_all.py`](file:///d:/PayGuard%20AI/backend/tests/run_all.py): Master test runner.
- [`backend/tests/test_ml_pipeline.py`](file:///d:/PayGuard%20AI/backend/tests/test_ml_pipeline.py): Probabilistic sampling, leakage checks, safe data splitting, and artifact loading unit tests.
- [`backend/tests/test_feature_engine.py`](file:///d:/PayGuard%20AI/backend/tests/test_feature_engine.py): Haversine distance & feature computation unit tests.
- [`backend/tests/test_policy_engine.py`](file:///d:/PayGuard%20AI/backend/tests/test_policy_engine.py): Policy priority & rule evaluation unit tests.
- [`backend/tests/test_api.py`](file:///d:/PayGuard%20AI/backend/tests/test_api.py): FastAPI REST integration tests.
- [`backend/tests/test_all_endpoints.py`](file:///d:/PayGuard%20AI/backend/tests/test_all_endpoints.py): Scenario integration tests.
