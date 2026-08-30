from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import FeatureVector, PolicyRule
from backend.app.services.policy_engine import policy_engine

def test_policy_engine_escalation(db_session):
    fv = FeatureVector(
        transaction_id="tx_dummy",
        amount=500.0,
        tx_amount_zscore=1.0,
        tx_velocity_1h=1,
        tx_velocity_24h=2,
        tx_amount_sum_24h=600.0,
        is_new_device=0,
        is_cross_border=0,
        time_since_last_tx_sec=3600.0,
        distance_from_home_km=5.0,
        mcc_risk_tier=2,
        ip_reputation_score=10.0,
        failed_otp_attempts_24h=0
    )

    # Risk Score 900 -> Should escalate to HOLD
    action_hold, triggers_hold = policy_engine.evaluate(db_session, fv, risk_score=900)
    assert action_hold == "HOLD"

    # Risk Score 750 -> Should require VERIFY
    action_verify, triggers_verify = policy_engine.evaluate(db_session, fv, risk_score=750)
    assert action_verify == "VERIFY"

    # Risk Score 300 -> Should APPROVE
    action_approve, triggers_approve = policy_engine.evaluate(db_session, fv, risk_score=300)
    assert action_approve == "APPROVE"
