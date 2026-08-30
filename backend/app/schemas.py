from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class TransactionCreateSchema(BaseModel):
    user_id: str = Field(..., example="usr_99812")
    merchant_id: str = Field(..., example="mer_4410")
    amount: float = Field(..., gt=0, example=1450.00)
    currency: str = Field("USD", example="USD")
    payment_method: str = Field("CREDIT_CARD", example="CREDIT_CARD")
    device_fingerprint: str = Field(..., example="dev_mac_8819ab")
    ip_address: str = Field(..., example="185.220.101.5")
    geo_location: str = Field("US-NY", example="US-NY")
    lat: Optional[float] = 40.7128
    lon: Optional[float] = -74.0060

class ShapAttributionSchema(BaseModel):
    feature: str
    label: str
    value: Any
    impact: str # "+0.34" or "-0.12"
    raw_shap_value: float
    direction: str # "INCREASES_RISK" or "REDUCES_RISK"
    description: str

class PolicyTriggerSchema(BaseModel):
    rule_id: str
    rule_name: str
    action: str
    description: str

class RiskEvaluationResponseSchema(BaseModel):
    transaction_id: str
    evaluated_at: str
    model_version: str
    risk_score: int # 0-1000
    raw_probability: float
    calibrated_probability: float
    risk_level: str # LOW, MEDIUM, HIGH, CRITICAL
    recommended_action: str # APPROVE, VERIFY, HOLD
    challenge_token: Optional[str] = None
    status: str
    explanations: List[ShapAttributionSchema]
    policy_triggers: List[PolicyTriggerSchema]
    natural_explanation: str

class VerifyChallengeSchema(BaseModel):
    transaction_id: str
    challenge_token: str
    otp_code: str

class VerifyChallengeResponseSchema(BaseModel):
    status: str
    transaction_id: str
    final_action: str
    audit_log_id: str
    message: str

class AnalystOverrideSchema(BaseModel):
    evaluation_id: str
    override_action: str # APPROVE, REJECT
    reason_code: str
    analyst_notes: str

class PolicyRuleCreateSchema(BaseModel):
    rule_name: str
    description: str
    priority: int = 10
    condition_json: Dict[str, Any]
    action: str # APPROVE, VERIFY, HOLD
    is_active: bool = True

class PolicyRuleResponseSchema(PolicyRuleCreateSchema):
    id: str
    created_at: str
    updated_at: str

class AuditLogResponseSchema(BaseModel):
    id: str
    evaluation_id: str
    transaction_id: str
    actor_type: str
    actor_id: str
    action_taken: str
    previous_state: Optional[str]
    new_state: str
    notes: Optional[str]
    timestamp: str

class ModelMetricsResponseSchema(BaseModel):
    dataset_type: Optional[str] = "Synthetic benchmark — generated dataset"
    label_generation_method: Optional[str] = "Probabilistic Bernoulli sampling (np.random.binomial)"
    seed: Optional[int] = 42
    n_samples_total: Optional[int] = 25000
    n_legitimate: Optional[int] = 23790
    n_fraud: Optional[int] = 1210
    fraud_prevalence: float
    n_train: int
    n_val: Optional[int] = 3750
    n_test: int
    model_type: str
    roc_auc: float
    pr_auc: Optional[float] = 0.2684
    brier_score_raw: float
    brier_score_calibrated: float
    ece_raw: float
    ece_calibrated: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: Dict[str, int]
    calibration_curve: List[Dict[str, Any]]
    precision_recall_curve: Optional[List[Dict[str, Any]]] = None
    global_feature_importance: List[Dict[str, Any]]
    feature_names: List[str]
    feature_labels: Dict[str, str]

# Public Benchmark Prediction Schemas
class PublicPredictionRequestSchema(BaseModel):
    Time: float = Field(0.0, description="Relative transaction timestamp in seconds")
    V1: float = Field(0.0, description="PCA-transformed numerical component V1")
    V2: float = Field(0.0, description="PCA-transformed numerical component V2")
    V3: float = Field(0.0, description="PCA-transformed numerical component V3")
    V4: float = Field(0.0, description="PCA-transformed numerical component V4")
    V5: float = Field(0.0, description="PCA-transformed numerical component V5")
    V6: float = Field(0.0, description="PCA-transformed numerical component V6")
    V7: float = Field(0.0, description="PCA-transformed numerical component V7")
    V8: float = Field(0.0, description="PCA-transformed numerical component V8")
    V9: float = Field(0.0, description="PCA-transformed numerical component V9")
    V10: float = Field(0.0, description="PCA-transformed numerical component V10")
    V11: float = Field(0.0, description="PCA-transformed numerical component V11")
    V12: float = Field(0.0, description="PCA-transformed numerical component V12")
    V13: float = Field(0.0, description="PCA-transformed numerical component V13")
    V14: float = Field(0.0, description="PCA-transformed numerical component V14")
    V15: float = Field(0.0, description="PCA-transformed numerical component V15")
    V16: float = Field(0.0, description="PCA-transformed numerical component V16")
    V17: float = Field(0.0, description="PCA-transformed numerical component V17")
    V18: float = Field(0.0, description="PCA-transformed numerical component V18")
    V19: float = Field(0.0, description="PCA-transformed numerical component V19")
    V20: float = Field(0.0, description="PCA-transformed numerical component V20")
    V21: float = Field(0.0, description="PCA-transformed numerical component V21")
    V22: float = Field(0.0, description="PCA-transformed numerical component V22")
    V23: float = Field(0.0, description="PCA-transformed numerical component V23")
    V24: float = Field(0.0, description="PCA-transformed numerical component V24")
    V25: float = Field(0.0, description="PCA-transformed numerical component V25")
    V26: float = Field(0.0, description="PCA-transformed numerical component V26")
    V27: float = Field(0.0, description="PCA-transformed numerical component V27")
    V28: float = Field(0.0, description="PCA-transformed numerical component V28")
    Amount: float = Field(..., ge=0, description="Transaction Amount ($)", example=149.99)
    include_explanations: Optional[bool] = Field(False, description="Set True to include SHAP local feature attributions")

class PublicShapAttributionSchema(BaseModel):
    feature: str
    feature_type: str = "PCA-transformed component"
    feature_value: float
    shap_value: float
    direction: str

class PublicPredictionResponseSchema(BaseModel):
    model_version: str = "v1.0.0"
    dataset_source: str = "public"
    dataset_type: str = "Public benchmark — locally supplied dataset"
    raw_probability: float
    calibrated_probability: float
    threshold: float = 0.5
    threshold_source: str = "fixed_default_0.5"
    calibration_method: str = "isotonic"
    decision: str
    top_positive_features: Optional[List[PublicShapAttributionSchema]] = None
    top_negative_features: Optional[List[PublicShapAttributionSchema]] = None
