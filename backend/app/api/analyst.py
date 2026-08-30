from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import RiskEvaluation, Transaction, User, Merchant
from backend.app.schemas import AnalystOverrideSchema
from backend.app.services.audit_service import audit_service

router = APIRouter(prefix="/api/v1/analyst", tags=["Analyst Review Queue"])

@router.get("/queue")
def get_analyst_queue(
    status_filter: Optional[str] = Query("ESCALATED_TO_ANALYST"),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(RiskEvaluation)
    if status_filter and status_filter != "ALL":
        query = query.filter(RiskEvaluation.status == status_filter)

    evaluations = query.order_by(RiskEvaluation.evaluated_at.desc()).limit(limit).all()

    result = []
    for ev in evaluations:
        tx = db.query(Transaction).filter(Transaction.id == ev.transaction_id).first()
        user = db.query(User).filter(User.id == tx.user_id).first() if tx else None
        merchant = db.query(Merchant).filter(Merchant.id == tx.merchant_id).first() if tx else None

        result.append({
            "evaluation_id": ev.id,
            "transaction_id": ev.transaction_id,
            "evaluated_at": ev.evaluated_at.isoformat(),
            "amount": tx.amount if tx else 0.0,
            "currency": tx.currency if tx else "USD",
            "payment_method": tx.payment_method if tx else "UNKNOWN",
            "user_id": tx.user_id if tx else "UNKNOWN",
            "user_email": user.email if user else "UNKNOWN",
            "merchant_name": merchant.name if merchant else "UNKNOWN",
            "merchant_mcc_tier": merchant.mcc_risk_tier if merchant else 1,
            "risk_score": ev.risk_score,
            "calibrated_probability": ev.calibrated_probability,
            "raw_probability": ev.raw_probability,
            "decision_action": ev.decision_action,
            "status": ev.status,
            "device_fingerprint": tx.device_fingerprint if tx else "",
            "ip_address": tx.ip_address if tx else "",
            "geo_location": tx.geo_location if tx else "",
            "shap_attributions": ev.shap_attributions,
            "triggered_policy_rules": ev.triggered_policy_rules,
            "natural_explanation": ev.natural_explanation,
            "analyst_notes": ev.analyst_notes
        })

    return result

@router.post("/override")
def analyst_override(payload: AnalystOverrideSchema, db: Session = Depends(get_db)):
    ev = db.query(RiskEvaluation).filter(RiskEvaluation.id == payload.evaluation_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation record not found.")

    prev_state = ev.status
    new_status = f"OVERRIDDEN_{payload.override_action.upper()}"
    ev.status = new_status
    ev.decision_action = payload.override_action.upper()
    ev.analyst_notes = payload.analyst_notes
    db.commit()

    log = audit_service.log_event(
        db=db,
        evaluation_id=ev.id,
        actor_type="ANALYST",
        actor_id="ANALYST_AGENT_01",
        action_taken=f"MANUAL_OVERRIDE_{payload.override_action.upper()}",
        previous_state=prev_state,
        new_state=new_status,
        notes=f"Reason: {payload.reason_code}. Notes: {payload.analyst_notes}"
    )

    return {
        "status": "SUCCESS",
        "evaluation_id": ev.id,
        "new_status": new_status,
        "final_action": ev.decision_action,
        "audit_log_id": log.id
    }
