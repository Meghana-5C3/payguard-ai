import uuid
from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import User, Merchant, Transaction, RiskEvaluation
from backend.app.schemas import (
    TransactionCreateSchema, RiskEvaluationResponseSchema,
    VerifyChallengeSchema, VerifyChallengeResponseSchema
)
from backend.app.services.feature_engine import compute_transaction_features
from backend.app.services.inference_service import inference_service
from backend.app.services.shap_service import shap_service
from backend.app.services.policy_engine import policy_engine
from backend.app.services.audit_service import audit_service

router = APIRouter(prefix="/api/v1/risk", tags=["Risk Evaluation"])

def ensure_user_and_merchant(db: Session, user_id: str, merchant_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, email=f"{user_id}@example.com", name=f"User {user_id}", risk_segment="STANDARD")
        db.add(user)

    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        merchant = Merchant(id=merchant_id, name="Global Retail Inc", category_code="5411", mcc_risk_tier=2)
        db.add(merchant)

    db.commit()

@router.post("/evaluate", response_model=RiskEvaluationResponseSchema)
def evaluate_transaction(payload: TransactionCreateSchema, db: Session = Depends(get_db)):
    ensure_user_and_merchant(db, payload.user_id, payload.merchant_id)

    # 1. Create Transaction
    tx = Transaction(
        user_id=payload.user_id,
        merchant_id=payload.merchant_id,
        amount=payload.amount,
        currency=payload.currency,
        payment_method=payload.payment_method,
        device_fingerprint=payload.device_fingerprint,
        ip_address=payload.ip_address,
        geo_location=payload.geo_location,
        lat=payload.lat,
        lon=payload.lon,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # 2. Compute Features
    fv = compute_transaction_features(db, tx)

    # 3. Predict & Calibrate
    inf_res = inference_service.predict(fv)

    # 4. SHAP Attributions & Explanations
    shap_res = shap_service.explain(inf_res["X_df"])

    # 5. Policy Engine
    recommended_action, policy_triggers = policy_engine.evaluate(db, fv, inf_res["risk_score"])

    # Challenge token if VERIFY required
    challenge_token = f"chk_tok_{uuid.uuid4().hex[:12]}" if recommended_action == "VERIFY" else None
    eval_status = "PENDING_VERIFICATION" if recommended_action == "VERIFY" else ("ESCALATED_TO_ANALYST" if recommended_action == "HOLD" else "COMPLETED")

    # 6. Save Risk Evaluation
    evaluation = RiskEvaluation(
        transaction_id=tx.id,
        model_version="v1.0.0-xgboost-isotonic",
        raw_probability=inf_res["raw_probability"],
        calibrated_probability=inf_res["calibrated_probability"],
        risk_score=inf_res["risk_score"],
        decision_action=recommended_action,
        challenge_token=challenge_token,
        triggered_policy_rules=policy_triggers,
        shap_attributions=shap_res["attributions"],
        natural_explanation=shap_res["natural_explanation"],
        status=eval_status,
        evaluated_at=datetime.now(timezone.utc)
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    # 7. Audit Log
    audit_service.log_event(
        db=db,
        evaluation_id=evaluation.id,
        actor_type="SYSTEM",
        actor_id="RISK_ENGINE_V1",
        action_taken=f"INITIAL_EVALUATION_{recommended_action}",
        previous_state=None,
        new_state=eval_status,
        notes=f"Risk Score: {inf_res['risk_score']}/1000. Calibrated Probability: {inf_res['calibrated_probability']:.2%}."
    )

    return RiskEvaluationResponseSchema(
        transaction_id=tx.id,
        evaluated_at=evaluation.evaluated_at.isoformat(),
        model_version=evaluation.model_version,
        risk_score=evaluation.risk_score,
        raw_probability=evaluation.raw_probability,
        calibrated_probability=evaluation.calibrated_probability,
        risk_level=inf_res["risk_level"],
        recommended_action=recommended_action,
        challenge_token=challenge_token,
        status=eval_status,
        explanations=shap_res["attributions"],
        policy_triggers=policy_triggers,
        natural_explanation=shap_res["natural_explanation"]
    )

@router.post("/verify", response_model=VerifyChallengeResponseSchema)
def verify_challenge(payload: VerifyChallengeSchema, db: Session = Depends(get_db)):
    evaluation = db.query(RiskEvaluation).filter(
        RiskEvaluation.transaction_id == payload.transaction_id
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Transaction risk evaluation not found.")

    if evaluation.status != "PENDING_VERIFICATION":
        raise HTTPException(status_code=400, detail=f"Transaction cannot be verified. Current status: {evaluation.status}")

    if evaluation.challenge_token != payload.challenge_token:
        raise HTTPException(status_code=403, detail="Invalid challenge verification token.")

    # Simulated verification logic (accepts any 6-digit OTP code or '123456')
    if len(payload.otp_code) != 6 or not payload.otp_code.isdigit():
        raise HTTPException(status_code=400, detail="OTP code must be a 6-digit number.")

    prev_state = evaluation.status
    evaluation.status = "COMPLETED"
    evaluation.decision_action = "APPROVE"
    db.commit()

    log = audit_service.log_event(
        db=db,
        evaluation_id=evaluation.id,
        actor_type="CUSTOMER",
        actor_id=payload.transaction_id,
        action_taken="VERIFY_OTP_SUCCESS",
        previous_state=prev_state,
        new_state="COMPLETED",
        notes=f"Customer successfully solved 2FA challenge with OTP {payload.otp_code[:2]}****"
    )

    return VerifyChallengeResponseSchema(
        status="SUCCESS",
        transaction_id=payload.transaction_id,
        final_action="APPROVE",
        audit_log_id=log.id,
        message="Verification successful. Transaction approved."
    )
