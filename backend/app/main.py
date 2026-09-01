import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User, Merchant
from backend.app.api import risk, analyst, policies, metrics, audit, public_predict

# Initialize database schema safely
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[Database] WARNING: Could not create database schema: {e}")

app = FastAPI(
    title="PAYGUARD AI - Explainable Adaptive Transaction Risk Manager",
    description="Enterprise-grade transaction risk evaluation backend with XGBoost + Isotonic Calibration + SHAP local explanations and dynamic policy engine.",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed baseline demo entities on startup
@app.on_event("startup")
def startup_db_seed():
    try:
        db = SessionLocal()
        try:
            if db.query(User).count() == 0:
                demo_users = [
                    User(id="usr_99812", email="alex.rivera@example.com", name="Alex Rivera", risk_segment="STANDARD", home_country="US", home_lat=40.7128, home_lon=-74.0060),
                    User(id="usr_55102", email="sarah.chen@example.com", name="Sarah Chen", risk_segment="VIP", home_country="US", home_lat=37.7749, home_lon=-122.4194),
                    User(id="usr_11094", email="devon.vance@example.com", name="Devon Vance", risk_segment="HIGH_RISK", home_country="CA", home_lat=43.6532, home_lon=-79.3832),
                ]
                db.add_all(demo_users)

            if db.query(Merchant).count() == 0:
                demo_merchants = [
                    Merchant(id="mer_4410", name="Coffee & Bakery Co.", category_code="5411", mcc_risk_tier=1, country="US"),
                    Merchant(id="mer_8820", name="Global Electronics Direct", category_code="5732", mcc_risk_tier=3, country="US"),
                    Merchant(id="mer_9950", name="Apex Crypto Vault", category_code="6051", mcc_risk_tier=5, country="US"),
                    Merchant(id="mer_1020", name="Luxury Watch Boutique", category_code="5094", mcc_risk_tier=4, country="GB"),
                ]
                db.add_all(demo_merchants)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"[Database] WARNING: Startup DB seed failed: {e}")

# Include routers
app.include_router(risk.router)
app.include_router(analyst.router)
app.include_router(policies.router)
app.include_router(metrics.router)
app.include_router(audit.router)
app.include_router(public_predict.router)

@app.get("/")
def root():
    return {
        "system": "PAYGUARD AI Engine",
        "status": "HEALTHY",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "payguard-ai-api",
        "version": "1.0.0"
    }
