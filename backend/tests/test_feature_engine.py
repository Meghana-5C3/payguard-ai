from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import User, Merchant, Transaction
from backend.app.services.feature_engine import compute_transaction_features, calculate_haversine_distance

def test_haversine_distance():
    dist = calculate_haversine_distance(40.7128, -74.0060, 37.7749, -122.4194)
    assert 4100 < dist < 4200

def test_feature_computation(db_session):
    tx = Transaction(
        user_id="usr_test",
        merchant_id="mer_test",
        amount=150.0,
        currency="USD",
        payment_method="CREDIT_CARD",
        device_fingerprint="dev_123",
        ip_address="192.168.1.1",
        geo_location="US-NY",
        lat=40.7128,
        lon=-74.0060
    )
    db_session.add(tx)
    db_session.commit()

    fv = compute_transaction_features(db_session, tx)
    assert fv.amount == 150.0
    assert fv.tx_velocity_1h == 0
    assert fv.is_cross_border == 0
    assert fv.distance_from_home_km == 0.0
