# PayGuard AI

## Explainable & Adaptive Transaction Risk Manager

PayGuard AI is an AI-powered transaction risk management system designed to detect potentially fraudulent transactions, estimate transaction risk, explain model decisions, and support analyst review workflows.

The system combines machine learning, probability calibration, explainable AI, policy-based evaluation, audit logging, and a web-based dashboard into a single full-stack application.

### Live Application

**Production:** https://payguard-ai-lilac.vercel.app/

### GitHub Repository

https://github.com/Meghana-5C3/payguard-ai

---

## Key Features

* AI-based transaction risk prediction
* Fraud-risk scoring and risk-level classification
* Probability calibration using an isotonic calibrator
* SHAP-based explainable AI
* Transaction policy evaluation
* Analyst review queue
* Analyst overrides
* Audit logging
* Model performance metrics
* Public fraud benchmark prediction
* REST APIs with FastAPI
* React dashboard
* Serverless deployment on Vercel

---

## System Architecture

```text
                    ┌─────────────────────────┐
                    │      React Frontend     │
                    │       Vite + TS         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI APIs       │
                    │      Python Backend     │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
   ┌─────────────┐      ┌────────────────┐      ┌──────────────┐
   │ Risk Engine │      │ Policy Engine  │      │ Audit/Analyst│
   └──────┬──────┘      └────────────────┘      └──────────────┘
          │
          ▼
   ┌───────────────────────────────┐
   │ XGBoost + Calibration + SHAP │
   └──────────────┬────────────────┘
                  │
                  ▼
            Risk Assessment
```

---

## Technology Stack

### Frontend

* React
* TypeScript
* Vite
* HTML5
* CSS
* JavaScript

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* SQLite

### Machine Learning

* XGBoost
* Scikit-learn
* Pandas
* NumPy
* Joblib
* SHAP

### Deployment

* Vercel
* Vercel Serverless Functions
* GitHub

---

## Machine Learning Pipeline

The project contains two prediction workflows.

### 1. Public Benchmark Pipeline

The public benchmark model uses the existing frozen model artifacts located at:

```text
backend/app/ml/artifacts/public/v1.0.0/
```

The benchmark feature set contains:

```text
Time
V1 ... V28
Amount
```

`V1`–`V28` are PCA-transformed numerical components.

The pipeline uses:

```text
Input Features
      ↓
Preprocessing
      ↓
XGBoost Model
      ↓
Probability Calibration
      ↓
Fraud Probability
      ↓
Decision
```

### 2. Synthetic Transaction Risk Pipeline

The application also provides a transaction-level risk workflow for evaluating application transactions.

This workflow integrates:

* ML risk prediction
* Probability calibration
* SHAP explanations
* Policy evaluation
* Database recording
* Audit logging
* Analyst review

---

## Model Integrity

The production benchmark model is treated as a frozen artifact.

The following were preserved:

* Trained XGBoost model
* Isotonic probability calibrator
* Preprocessing artifacts
* Threshold: `0.5`
* Benchmark evaluation metrics

No retraining or recalibration is performed during deployment.

### Benchmark Metrics

| Metric    |  Value |
| --------- | -----: |
| PR-AUC    | 0.7842 |
| ROC-AUC   | 0.9586 |
| Precision | 0.9423 |
| Recall    | 0.6622 |
| F1 Score  | 0.7778 |

---

## Explainable AI

PayGuard AI uses SHAP-based explanations to identify important factors contributing to a transaction risk decision.

The system provides:

* Feature-level attributions
* Top risk drivers
* Human-readable explanations

This helps analysts understand **why** a transaction received a particular risk assessment instead of relying only on a prediction score.

---

## Main API Endpoints

### Health

```http
GET /health
```

Returns service health and version information.

### Risk Evaluation

```http
POST /api/v1/risk/evaluate
```

Evaluates a transaction and returns risk information, explanations, recommended action, and policy triggers.

### Analyst Queue

```http
GET /api/v1/analyst/queue
```

Retrieves transactions requiring analyst review.

### Analyst Override

```http
POST /api/v1/analyst/override
```

Allows an analyst to override the recommended transaction action.

### Policies

```http
GET /api/v1/policies
POST /api/v1/policies/reset-defaults
PUT /api/v1/policies/{rule_id}
```

Manage transaction risk policies.

### Performance Metrics

```http
GET /api/v1/metrics/performance
```

Returns model performance information.

### Audit Logs

```http
GET /api/v1/audit/logs
```

Retrieves transaction and analyst audit information.

### Public Prediction

```http
POST /api/public/predict
```

Runs the public benchmark prediction pipeline.

### Documentation

```text
/docs
/openapi.json
```

Interactive Swagger documentation and OpenAPI specification.

---

## Example Risk Request

```json
{
  "user_id": "usr_test_001",
  "merchant_id": "mer_test_001",
  "amount": 1450,
  "currency": "USD",
  "payment_method": "CREDIT_CARD",
  "device_fingerprint": "dev_test_001",
  "ip_address": "127.0.0.1",
  "geo_location": "US-NY",
  "lat": 40.7128,
  "lon": -74.0060
}
```

---

## Example Response

```json
{
  "transaction_id": "...",
  "risk_score": 76,
  "raw_probability": 0.9767,
  "calibrated_probability": 0.6949,
  "recommended_action": "APPROVE",
  "status": "COMPLETED",
  "explanations": [],
  "policy_triggers": []
}
```

---

## Project Structure

```text
payguard-ai/
│
├── api/
│   ├── analyst/
│   ├── audit/
│   ├── docs/
│   ├── health/
│   ├── metrics/
│   ├── policies/
│   ├── public_predict/
│   └── risk/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ml/
│   │   │   └── artifacts/
│   │   ├── services/
│   │   ├── database.py
│   │   ├── main.py
│   │   └── schemas.py
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── api/
├── requirements.txt
├── package.json
├── vercel.json
├── .python-version
└── README.md
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Meghana-5C3/payguard-ai.git
cd payguard-ai
```

### 2. Create a Python virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start the backend

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 5. Install frontend dependencies

Open another terminal:

```powershell
cd frontend
npm install
```

### 6. Start the frontend

```powershell
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

## Production Deployment

The application is deployed using Vercel.

The production frontend and backend are served through the same Vercel project:

```text
https://payguard-ai-lilac.vercel.app/
```

The frontend communicates with the backend through same-origin API paths such as:

```text
/api/v1/...
/api/public/...
```

---

## Testing

Before deployment, the major application components were verified locally, including:

* Health check
* Risk evaluation
* Analyst queue
* Analyst override
* Policy management
* Performance metrics
* Audit logs
* Public benchmark prediction
* Swagger/OpenAPI
* Frontend production build

Example:

```text
GET  /health                     → 200 OK
POST /api/v1/risk/evaluate       → 200 OK
GET  /api/v1/analyst/queue       → 200 OK
POST /api/v1/analyst/override    → 200 OK
GET  /api/v1/policies            → 200 OK
GET  /api/v1/metrics/performance → 200 OK
GET  /api/v1/audit/logs          → 200 OK
POST /api/public/predict         → 200 OK
GET  /docs                       → 200 OK
GET  /openapi.json               → 200 OK
```

---

## Security & Deployment Considerations

* Production ML artifacts are frozen.
* The public benchmark dataset is not required at runtime for prediction.
* Serverless database initialization is handled for isolated Vercel functions.
* API routes are separated into individual serverless functions.
* Sensitive credentials should be stored using environment variables rather than committed to Git.
* Production deployment access should be configured so the public application can be accessed without requiring visitors to log into Vercel.

---

## Future Enhancements

Potential future improvements include:

* Streaming transaction monitoring
* Advanced analyst workflows
* Additional fraud detection models
* Real-time alerting
* Role-based access control
* Cloud database integration
* Model monitoring and drift detection
* Additional explainability visualizations

---

## Project Objective

PayGuard AI aims to demonstrate how machine learning can be integrated into a practical financial-risk workflow while keeping predictions interpretable, auditable, and usable by human analysts.

The project combines:

**Prediction + Calibration + Explainability + Policies + Analyst Review + Auditing**

into one end-to-end transaction risk management platform.

---

## Author

**Meghana Chedulla**

B.Tech – Computer Science & Engineering

GitHub: https://github.com/Meghana-5C3
