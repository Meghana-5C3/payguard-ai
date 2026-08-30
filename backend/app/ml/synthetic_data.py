import numpy as np
import pandas as pd

FEATURE_NAMES = [
    "amount",
    "tx_amount_zscore",
    "tx_velocity_1h",
    "tx_velocity_24h",
    "tx_amount_sum_24h",
    "is_new_device",
    "is_cross_border",
    "time_since_last_tx_sec",
    "distance_from_home_km",
    "mcc_risk_tier",
    "ip_reputation_score",
    "failed_otp_attempts_24h",
]

def generate_synthetic_dataset(n_samples=25000, seed=42) -> pd.DataFrame:
    """
    Generates synthetic transaction feature vectors with realistic domain risk signals
    and probabilistic (Bernoulli) label sampling using numpy default_rng.
    
    Guarantees:
    - No transaction_id or user_id features.
    - No feature directly reveals the target label.
    - Generated probabilities are NOT returned as model features.
    - Fully deterministic given the same seed.
    """
    rng = np.random.default_rng(seed)

    # 1. Feature distributions (independent from final label)
    amount = rng.exponential(scale=120, size=n_samples) + 5
    tx_amount_zscore = rng.normal(loc=0, scale=1.0, size=n_samples)
    tx_velocity_1h = rng.poisson(lam=0.8, size=n_samples)
    tx_velocity_24h = tx_velocity_1h + rng.poisson(lam=3.5, size=n_samples)
    tx_amount_sum_24h = amount + rng.exponential(scale=300, size=n_samples)
    
    is_new_device = rng.binomial(n=1, p=0.15, size=n_samples)
    is_cross_border = rng.binomial(n=1, p=0.08, size=n_samples)
    time_since_last_tx_sec = rng.exponential(scale=86400, size=n_samples) + 10
    distance_from_home_km = rng.exponential(scale=25, size=n_samples)
    mcc_risk_tier = rng.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.45, 0.30, 0.15, 0.07, 0.03])
    ip_reputation_score = rng.beta(a=0.5, b=5.0, size=n_samples) * 100
    failed_otp_attempts_24h = rng.poisson(lam=0.1, size=n_samples)

    # 2. Latent risk log-odds formula with domain interaction terms
    risk_signal = (
        -4.8  # Baseline log-odds (~3% to 5% fraud prevalence)
        + 0.90 * np.maximum(0, tx_amount_zscore - 1.2)
        + 1.10 * np.maximum(0, tx_velocity_1h - 2)
        + 1.40 * is_new_device
        + 1.00 * is_cross_border
        + 0.75 * (mcc_risk_tier - 2)
        + 0.045 * ip_reputation_score
        + 1.60 * failed_otp_attempts_24h
        + 2.10 * (is_new_device * (tx_velocity_1h >= 3))
        + 1.80 * (is_cross_border * (ip_reputation_score > 70))
        + 1.60 * ((tx_amount_zscore > 2.5) * is_new_device)
        + 2.20 * ((failed_otp_attempts_24h > 1) * (mcc_risk_tier >= 4))
    )

    # Sigmoid function converting log-odds to continuous probability
    probabilities = 1.0 / (1.0 + np.exp(-risk_signal))

    # PROBABILISTIC BERNOULLI SAMPLING using default_rng
    labels = rng.binomial(1, probabilities)

    df = pd.DataFrame({
        "amount": amount,
        "tx_amount_zscore": tx_amount_zscore,
        "tx_velocity_1h": tx_velocity_1h,
        "tx_velocity_24h": tx_velocity_24h,
        "tx_amount_sum_24h": tx_amount_sum_24h,
        "is_new_device": is_new_device,
        "is_cross_border": is_cross_border,
        "time_since_last_tx_sec": time_since_last_tx_sec,
        "distance_from_home_km": distance_from_home_km,
        "mcc_risk_tier": mcc_risk_tier,
        "ip_reputation_score": ip_reputation_score,
        "failed_otp_attempts_24h": failed_otp_attempts_24h,
        "is_fraud": labels
    })
    return df
