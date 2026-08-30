from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

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
