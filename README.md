# 🛡️ PayGuard AI

## Explainable & Adaptive Transaction Risk Manager

> **An AI-powered fintech risk intelligence platform that detects transaction risk, explains every decision, applies business policies, and enables human analyst intervention.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-PayGuard%20AI-00A8E8?style=for-the-badge)](https://payguard-ai-lilac.vercel.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge\&logo=github)](https://github.com/Meghana-5C3/payguard-ai)

---

## 🚀 What is PayGuard AI?

Payment fraud detection cannot stop at **"Fraud"** or **"Legitimate."**

A practical financial-risk system must also answer:

* How risky is this transaction?
* Why was it considered risky?
* Which factors influenced the decision?
* Should the transaction be approved, challenged, or reviewed?
* Can an analyst intervene?
* Can the decision be audited later?

**PayGuard AI** was built to address this complete workflow.

It combines **machine learning, probability calibration, explainable AI, policy evaluation, analyst review, and auditability** into a single full-stack application.

---

## 🎯 Problem Statement

Modern digital payment systems process large numbers of transactions where fraudulent activity can be difficult to identify using fixed business rules alone.

At the same time, a black-box ML prediction creates another problem:

> **A prediction without an explanation is difficult to trust, review, and act upon.**

PayGuard AI addresses both challenges by combining predictive intelligence with explainability and human oversight.

---

## 💡 Solution

PayGuard AI follows an end-to-end transaction risk workflow:

```text
                    Transaction
                         │
                         ▼
                ┌─────────────────┐
                │ Feature Engine  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   XGBoost Model  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Probability     │
                │ Calibration     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Risk Assessment  │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
      ┌───────────────┐     ┌────────────────┐
      │ SHAP Explain. │     │ Policy Engine  │
      └───────┬───────┘     └───────┬────────┘
              │                     │
              └──────────┬──────────┘
                         ▼
                ┌─────────────────┐
                │ Final Decision  │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Analyst Review          Audit Log
```

---

# ✨ Key Features

### 🤖 AI-Powered Risk Detection

Uses an XGBoost-based classification pipeline to estimate transaction risk.

### 📊 Probability Calibration

Uses an **isotonic calibration layer** to improve the reliability of predicted probabilities.

### 🔍 Explainable AI

Uses **SHAP-based explanations** to identify important factors contributing to a risk decision.

### ⚙️ Policy Engine

Combines ML-based risk assessment with configurable business rules.

### 👨‍💻 Analyst Review

Provides an analyst queue for reviewing transactions that require human intervention.

### 🔄 Analyst Override

Authorized analysts can override the recommended action when business context requires it.

### 🧾 Auditability

Important transaction and analyst actions are recorded for traceability.

### 📈 Model Performance Monitoring

Provides access to benchmark model performance metrics through the application.

### 🌐 Public Benchmark API

Provides a separate endpoint for evaluating the frozen public fraud benchmark pipeline.

### 🖥️ Full-Stack Dashboard

A React-based interface provides an interactive view of transaction risk, explanations, policies, analysts, metrics, and audit information.

---

# 🧠 Machine Learning

PayGuard AI contains two prediction workflows.

## 1. Public Benchmark Pipeline

The public benchmark pipeline uses the existing frozen model artifacts located at:

```text
backend/app/ml/artifacts/public/v1.0.0/
```

The benchmark contains:

```text
Time
V1 ... V28
Amount
```

`V1`–`V28` represent **PCA-transformed numerical components**.

The public pipeline is:

```text
Input
  ↓
Preprocessing
  ↓
XGBoost
  ↓
Isotonic Calibration
  ↓
Fraud Probability
  ↓
Threshold Decision
```

### Frozen Benchmark Configuration

| Metric             |      Value |
| ------------------ | ---------: |
| PR-AUC             | **0.7842** |
| ROC-AUC            | **0.9586** |
| Precision          | **0.9423** |
| Recall             | **0.6622** |
| F1 Score           | **0.7778** |
| Decision Threshold |    **0.5** |

The production benchmark pipeline does not retrain or recalibrate the model during deployment.

---

# 🔬 Explainable AI

A major design goal of PayGuard AI is to make model decisions understandable.

Instead of returning only:

```text
Risk = HIGH
```

the system provides feature-level explanations through SHAP.

Conceptually:

```text
Transaction
     ↓
Model Prediction
     ↓
SHAP Analysis
     ↓
Top Contributing Factors
     ↓
Human-Readable Explanation
```

This makes the system more useful for analysts and demonstrates how AI decisions can be integrated into human decision-making workflows.

---

# 🏦 Fintech Workflow

PayGuard AI is designed around a practical payment-risk lifecycle:

```text
Transaction Received
        ↓
Risk Prediction
        ↓
Probability Calibration
        ↓
Explainability
        ↓
Policy Evaluation
        ↓
Recommended Action
        ↓
Analyst Review (when required)
        ↓
Override / Confirmation
        ↓
Audit Record
```

This connects **AI prediction** with **business operations** rather than treating fraud detection as an isolated ML problem.

---

# 🧩 Technology Stack

## Frontend

* React
* TypeScript
* Vite
* HTML5
* CSS

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* SQLite

## Machine Learning

* XGBoost
* Scikit-learn
* Pandas
* NumPy
* Joblib
* SHAP

## Deployment

* Vercel
* Vercel Serverless Functions
* GitHub

---

# 🏗️ Architecture

```text
┌─────────────────────────────────────────┐
│              React Frontend              │
│          TypeScript + Vite               │
└────────────────────┬────────────────────┘
                     │
                     │ REST API
                     ▼
┌─────────────────────────────────────────┐
│               FastAPI                    │
│        Serverless API Functions          │
└────────────────────┬────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   Risk Engine   Policy Engine  Analyst/Audit
        │
        ▼
┌─────────────────────────────────────────┐
│          ML + Explainability             │
│                                          │
│  XGBoost → Calibration → SHAP            │
└─────────────────────────────────────────┘
                     │
                     ▼
              SQLite Database
```

---

# 🔌 API Endpoints

## Health

```http
GET /health
```

Returns application health and version information.

## Risk Evaluation

```http
POST /api/v1/risk/evaluate
```

Evaluates a transaction and returns risk information, recommended action, explanations, and policy triggers.

## Analyst Queue

```http
GET /api/v1/analyst/queue
```

Retrieves transactions requiring analyst review.

## Analyst Override

```http
POST /api/v1/analyst/override
```

Allows an analyst to override the recommended action.

## Policies

```http
GET /api/v1/policies
POST /api/v1/policies/reset-defaults
PUT /api/v1/policies/{rule_id}
```

## Performance Metrics

```http
GET /api/v1/metrics/performance
```

## Audit Logs

```http
GET /api/v1/audit/logs
```

## Public Benchmark Prediction

```http
POST /api/public/predict
```

## API Documentation

```text
/docs
/openapi.json
```

---

# 📥 Example Transaction Request

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

# 📤 Example Response

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

# 📁 Project Structure

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
│   └── app/
│       ├── api/
│       ├── ml/
│       │   └── artifacts/
│       ├── services/
│       ├── database.py
│       ├── main.py
│       └── schemas.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── requirements.txt
├── package.json
├── vercel.json
├── .python-version
└── README.md
```

---

# 🛠️ Local Development

## Clone

```bash
git clone https://github.com/Meghana-5C3/payguard-ai.git
cd payguard-ai
```

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start FastAPI:

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

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# ✅ Verification

The application has been locally verified across the major backend and frontend workflows.

| Component                   | Status |
| --------------------------- | ------ |
| Health API                  | ✅      |
| Risk Evaluation             | ✅      |
| Analyst Queue               | ✅      |
| Analyst Override            | ✅      |
| Policy APIs                 | ✅      |
| Performance Metrics         | ✅      |
| Audit Logs                  | ✅      |
| Public Benchmark Prediction | ✅      |
| Swagger / OpenAPI           | ✅      |
| Frontend Build              | ✅      |
| ML Model Loading            | ✅      |
| Probability Calibration     | ✅      |
| SHAP Explanation            | ✅      |
| Database Initialization     | ✅      |

---

# 🌍 Live Demo

### Application

**https://payguard-ai-lilac.vercel.app/**

### API Documentation

**https://payguard-ai-lilac.vercel.app/docs**

### Health Check

**https://payguard-ai-lilac.vercel.app/health**

### Source Code

**https://github.com/Meghana-5C3/payguard-ai**

---

# 🔐 Design Principles

PayGuard AI was developed around five core principles:

### 1. Explainability

Risk predictions should be understandable.

### 2. Reliability

The application should provide more than a model score; it should support a complete transaction workflow.

### 3. Human-in-the-Loop

AI recommendations should support analysts rather than eliminate human oversight.

### 4. Auditability

Risk decisions and analyst actions should be traceable.

### 5. Model Integrity

The production benchmark model and calibrator are treated as frozen artifacts, avoiding accidental retraining or recalibration during deployment.

---

# ⚠️ Deployment Challenges

Building and deploying an AI-powered full-stack application introduced several practical engineering challenges.

### Serverless Runtime Isolation

Vercel serverless functions run in isolated environments. Dependencies and model artifacts therefore had to be resolved correctly for each function.

### ML Artifact Resolution

Model, calibration, preprocessing, and SHAP artifacts required robust path resolution so that inference remained reliable inside the serverless runtime.

### Database Initialization

Each serverless function may execute independently, so database initialization had to be reliable even when application startup hooks were not shared across invocations.

### API Routing

Frontend routes and individual serverless API functions required explicit routing to prevent SPA fallbacks from intercepting API requests.

### Dependency Isolation

Each scoped serverless function required its own dependencies. Missing `scikit-learn` initially caused the frozen isotonic calibration artifact to fail during deserialization.

These challenges were resolved without changing the underlying trained model, calibration strategy, threshold, or benchmark metrics.

---

# 🎓 What This Project Demonstrates

PayGuard AI demonstrates the integration of:

```text
Machine Learning
      +
Probability Calibration
      +
Explainable AI
      +
Business Rules
      +
Human Review
      +
Auditability
      +
Full-Stack Engineering
      +
Cloud Deployment
```

Rather than building only a fraud classifier, the project focuses on turning an ML prediction into an **operational transaction-risk decision system**.

---

# 🔮 Future Improvements

Potential next steps include:

* Real-time transaction streaming
* Advanced fraud pattern detection
* Automated anomaly detection
* Model drift monitoring
* Role-based analyst access
* Cloud database integration
* Real-time fraud alerts
* Additional explainability visualizations
* Model monitoring dashboards

---

# 👩‍💻 Author

## Meghana Chedulla

**B.Tech – Computer Science & Engineering**

GitHub:
https://github.com/Meghana-5C3

---

## ⭐ Project Vision

> **Make payment-risk decisions not only intelligent, but explainable, actionable, and auditable.**

PayGuard AI brings together AI prediction and human decision-making to create a practical foundation for trustworthy transaction-risk management.
