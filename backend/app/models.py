import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    risk_segment = Column(String, default="STANDARD")  # LOW_RISK, STANDARD, HIGH_RISK, VIP
    home_country = Column(String, default="US")
    home_lat = Column(Float, default=40.7128)
    home_lon = Column(Float, default=-74.0060)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="user")

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    category_code = Column(String, nullable=False) # MCC
    mcc_risk_tier = Column(Integer, default=1) # 1-5
    country = Column(String, default="US")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="merchant")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(String, default="CREDIT_CARD")
    device_fingerprint = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    geo_location = Column(String, default="US-NY")
    lat = Column(Float, default=40.7128)
    lon = Column(Float, default=-74.0060)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    feature_vector = relationship("FeatureVector", back_populates="transaction", uselist=False)
    risk_evaluation = relationship("RiskEvaluation", back_populates="transaction", uselist=False)

class FeatureVector(Base):
    __tablename__ = "feature_vectors"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    tx_amount_zscore = Column(Float, nullable=False)
    tx_velocity_1h = Column(Integer, nullable=False)
    tx_velocity_24h = Column(Integer, nullable=False)
    tx_amount_sum_24h = Column(Float, nullable=False)
    is_new_device = Column(Integer, nullable=False) # 0 or 1
    is_cross_border = Column(Integer, nullable=False) # 0 or 1
    time_since_last_tx_sec = Column(Float, nullable=False)
    distance_from_home_km = Column(Float, nullable=False)
    mcc_risk_tier = Column(Integer, nullable=False)
    ip_reputation_score = Column(Float, nullable=False)
    failed_otp_attempts_24h = Column(Integer, nullable=False)
    raw_features_json = Column(JSON, nullable=True)

    transaction = relationship("Transaction", back_populates="feature_vector")

class RiskEvaluation(Base):
    __tablename__ = "risk_evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), unique=True, nullable=False)
    model_version = Column(String, default="v1.0.0-xgboost")
    raw_probability = Column(Float, nullable=False)
    calibrated_probability = Column(Float, nullable=False)
    risk_score = Column(Integer, nullable=False) # 0-1000
    decision_action = Column(String, nullable=False) # APPROVE, VERIFY, HOLD
    challenge_token = Column(String, nullable=True)
    triggered_policy_rules = Column(JSON, nullable=True)
    shap_attributions = Column(JSON, nullable=True)
    natural_explanation = Column(Text, nullable=True)
    status = Column(String, default="COMPLETED") # COMPLETED, PENDING_VERIFICATION, ESCALATED_TO_ANALYST, OVERRIDDEN_APPROVED, OVERRIDDEN_REJECTED
    analyst_notes = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    transaction = relationship("Transaction", back_populates="risk_evaluation")
    audit_logs = relationship("AuditLog", back_populates="evaluation")

class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    rule_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=10) # lower number = higher priority
    condition_json = Column(JSON, nullable=False)
    action = Column(String, nullable=False) # APPROVE, VERIFY, HOLD
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    evaluation_id = Column(String, ForeignKey("risk_evaluations.id"), nullable=False)
    actor_type = Column(String, nullable=False) # SYSTEM, CUSTOMER, ANALYST
    actor_id = Column(String, nullable=False)
    action_taken = Column(String, nullable=False)
    previous_state = Column(String, nullable=True)
    new_state = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    evaluation = relationship("RiskEvaluation", back_populates="audit_logs")
