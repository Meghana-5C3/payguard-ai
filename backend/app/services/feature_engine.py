import math
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.models import User, Merchant, Transaction, FeatureVector

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in kilometers
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return float(R * c)

def compute_transaction_features(db: Session, transaction: Transaction) -> FeatureVector:
    user = db.query(User).filter(User.id == transaction.user_id).first()
    merchant = db.query(Merchant).filter(Merchant.id == transaction.merchant_id).first()

    # Query historical transactions for user in past 24h & 30d
    now = transaction.timestamp or datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    twenty_four_hours_ago = now - timedelta(days=1)
    thirty_days_ago = now - timedelta(days=30)

    user_txs_30d = db.query(Transaction).filter(
        Transaction.user_id == transaction.user_id,
        Transaction.timestamp >= thirty_days_ago,
        Transaction.id != transaction.id
    ).all()

    user_txs_1h = [tx for tx in user_txs_30d if tx.timestamp >= one_hour_ago]
    user_txs_24h = [tx for tx in user_txs_30d if tx.timestamp >= twenty_four_hours_ago]

    # Calculate velocities
    tx_velocity_1h = len(user_txs_1h)
    tx_velocity_24h = len(user_txs_24h)
    tx_amount_sum_24h = float(sum(tx.amount for tx in user_txs_24h) + transaction.amount)

    # Calculate Z-score
    amounts_30d = [tx.amount for tx in user_txs_30d]
    if len(amounts_30d) >= 3:
        mean_amt = float(sum(amounts_30d) / len(amounts_30d))
        std_amt = float(math.sqrt(sum((x - mean_amt) ** 2 for x in amounts_30d) / len(amounts_30d)))
        if std_amt < 1.0:
            std_amt = 1.0
        tx_amount_zscore = float((transaction.amount - mean_amt) / std_amt)
    else:
        # Default baseline if new user
        baseline_mean = 85.0
        baseline_std = 45.0
        tx_amount_zscore = float((transaction.amount - baseline_mean) / baseline_std)

    # Device fingerprint check
    known_devices = {tx.device_fingerprint for tx in user_txs_30d}
    is_new_device = 1 if (len(known_devices) > 0 and transaction.device_fingerprint not in known_devices) else 0

    # Cross-border check
    user_country = user.home_country if user else "US"
    merchant_country = merchant.country if merchant else "US"
    is_cross_border = 1 if user_country != merchant_country else 0

    # Time since last tx
    if user_txs_30d:
        latest_tx_time = max(tx.timestamp for tx in user_txs_30d)
        time_since_last_tx_sec = float((now - latest_tx_time).total_seconds())
    else:
        time_since_last_tx_sec = 86400.0 # 24 hours baseline

    # Haversine Distance from home
    home_lat = user.home_lat if user else 40.7128
    home_lon = user.home_lon if user else -74.0060
    distance_from_home_km = calculate_haversine_distance(
        home_lat, home_lon, transaction.lat or 40.7128, transaction.lon or -74.0060
    )

    # MCC Risk tier
    mcc_risk_tier = merchant.mcc_risk_tier if merchant else 2

    # IP Reputation (mock heuristics based on IP address string representation)
    ip_str = transaction.ip_address or "127.0.0.1"
    if "185.220" in ip_str or "109.70" in ip_str or "192.42" in ip_str: # Known proxy IP ranges
        ip_reputation_score = 92.0
    elif ip_str.startswith("10.") or ip_str.startswith("192.168.") or ip_str.startswith("127."):
        ip_reputation_score = 5.0
    else:
        # Deterministic mock score based on IP hash
        ip_reputation_score = float((hash(ip_str) % 40) + 10)

    failed_otp_attempts_24h = 0 # Default clean

    fv = FeatureVector(
        transaction_id=transaction.id,
        amount=float(transaction.amount),
        tx_amount_zscore=round(float(tx_amount_zscore), 4),
        tx_velocity_1h=int(tx_velocity_1h),
        tx_velocity_24h=int(tx_velocity_24h),
        tx_amount_sum_24h=round(float(tx_amount_sum_24h), 2),
        is_new_device=int(is_new_device),
        is_cross_border=int(is_cross_border),
        time_since_last_tx_sec=round(float(time_since_last_tx_sec), 1),
        distance_from_home_km=round(float(distance_from_home_km), 2),
        mcc_risk_tier=int(mcc_risk_tier),
        ip_reputation_score=round(float(ip_reputation_score), 1),
        failed_otp_attempts_24h=int(failed_otp_attempts_24h),
        raw_features_json={
            "amount": float(transaction.amount),
            "tx_amount_zscore": round(float(tx_amount_zscore), 4),
            "tx_velocity_1h": int(tx_velocity_1h),
            "tx_velocity_24h": int(tx_velocity_24h),
            "tx_amount_sum_24h": round(float(tx_amount_sum_24h), 2),
            "is_new_device": int(is_new_device),
            "is_cross_border": int(is_cross_border),
            "time_since_last_tx_sec": round(float(time_since_last_tx_sec), 1),
            "distance_from_home_km": round(float(distance_from_home_km), 2),
            "mcc_risk_tier": int(mcc_risk_tier),
            "ip_reputation_score": round(float(ip_reputation_score), 1),
            "failed_otp_attempts_24h": int(failed_otp_attempts_24h),
        }
    )

    db.add(fv)
    db.commit()
    db.refresh(fv)
    return fv
