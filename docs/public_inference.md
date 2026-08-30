# PayGuard AI - Public Benchmark Inference Service Documentation

**Document Status**: Production Specification  
**Model Version**: `v1.0.0`  
**Endpoint**: `POST /api/public/predict`  
**Last Updated**: August 27, 2026  

---

## 1. Purpose & Overview

The Public Benchmark Inference Service provides an isolated execution path for real-time inference using the frozen Public Fraud Benchmark model (trained on Kaggle `creditcard.csv`).

> [!IMPORTANT]
> **Research & Demonstration Disclaimer**:
> The public benchmark pipeline is intended for research, reproducibility, benchmarking, and demonstration. Its benchmark performance does not imply production payment-fraud detection capability.
> 
> Features `V1` through `V28` are PCA-transformed numerical components and do not directly correspond to business concepts such as device risk, IP reputation, transaction velocity, OTP failures, or merchant risk.

---

## 2. Model & Pipeline Specifications

- **Model Architecture**: Frozen `xgb.XGBClassifier` (`n_estimators=150`, `max_depth=5`, `learning_rate=0.06`, `scale_pos_weight=577.868`).
- **Preprocessor**: Frozen `StandardScaler` fitted on training set ONLY.
- **Probability Calibrator**: Frozen `ProbabilityCalibrator` (`selected_method: "isotonic"`).
- **Decision Threshold**: `0.5` (`threshold_source: "fixed_default_0.5"`).
- **Artifact Location**: `backend/app/ml/artifacts/public/v1.0.0/`

---

## 3. Required Input Features (30)

| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `Time` | `float` | Relative timestamp in seconds elapsed since the first transaction |
| `V1` .. `V28` | `float` | Anonymized PCA-transformed numerical components |
| `Amount` | `float` | Transaction amount ($) |

---

## 4. API Endpoint & Example Payload

### Request Endpoint:
`POST /api/public/predict`

### Example Request Body (JSON):
```json
{
  "Time": 406.0,
  "V1": -2.3122,
  "V2": 1.9519,
  "V3": -1.6098,
  "V4": 3.9979,
  "V5": -0.5221,
  "V6": -1.4265,
  "V7": -2.5373,
  "V8": 1.3916,
  "V9": -2.7700,
  "V10": -2.7722,
  "V11": 3.2020,
  "V12": -2.8999,
  "V13": -0.5952,
  "V14": -4.2892,
  "V15": 0.3897,
  "V16": -1.1407,
  "V17": -2.8300,
  "V18": -0.0168,
  "V19": 0.4169,
  "V20": 0.1269,
  "V21": 0.5172,
  "V22": -0.0350,
  "V23": -0.4652,
  "V24": 0.3201,
  "V25": 0.0445,
  "V26": 0.1778,
  "V27": 0.2611,
  "V28": -0.1432,
  "Amount": 0.0,
  "include_explanations": true
}
```

### Example Response Body (JSON):
```json
{
  "model_version": "v1.0.0",
  "dataset_source": "public",
  "dataset_type": "Public benchmark — locally supplied dataset",
  "raw_probability": 0.9998,
  "calibrated_probability": 0.9999,
  "threshold": 0.5,
  "threshold_source": "fixed_default_0.5",
  "calibration_method": "isotonic",
  "decision": "FRAUD",
  "top_positive_features": [
    {
      "feature": "V14",
      "feature_type": "PCA-transformed component",
      "feature_value": -4.2892,
      "shap_value": 3.8505,
      "direction": "INCREASES_FRAUD_RISK"
    },
    {
      "feature": "V4",
      "feature_type": "PCA-transformed component",
      "feature_value": 3.9979,
      "shap_value": 2.4708,
      "direction": "INCREASES_FRAUD_RISK"
    }
  ],
  "top_negative_features": [
    {
      "feature": "V13",
      "feature_type": "PCA-transformed component",
      "feature_value": -0.5952,
      "shap_value": -0.2387,
      "direction": "REDUCES_FRAUD_RISK"
    }
  ]
}
```

---

## 5. Architectural Separation

- **Synthetic Pipeline**: `/api/risk/evaluate` (Uses 12 domain features, isolated under `artifacts/v1.0.0/`).
- **Public Benchmark Pipeline**: `/api/public/predict` (Uses 30 PCA features, isolated under `artifacts/public/v1.0.0/`).
- **Zero Collision**: The synthetic demo pipeline and public benchmark pipeline remain completely isolated.

---

## 6. Frontend & Demo UI Integration

The Public Fraud Benchmark interface is integrated into the React frontend under the **Public Benchmark** navigation tab (`frontend/src/pages/PublicBenchmarkPage.tsx`).

### Capabilities:
1. **Interactive Parameter Form**: Allows input of all 30 public features (`Time`, `V1`..`V28`, `Amount`). Includes one-click quick-fill buttons (`Load Legit Sample`, `Load Fraud Sample`).
2. **Real-Time API Execution**: Dispatches requests to `POST /api/public/predict` via `api.predictPublicBenchmark()`.
3. **Calibrated Decision Display**: Highlights decision status (**`FRAUD`** vs **`LEGITIMATE`**), raw vs calibrated probabilities, and fixed threshold parameters (`0.5`).
4. **SHAP Attributions**: Renders local risk drivers with strict PCA neutral labels (`PCA-transformed component`).
5. **Frozen Benchmark Metrics Panel**: Displays held-out test evaluation metrics (PR-AUC: `0.7842`, ROC-AUC: `0.9586`, F1: `0.7778`).
