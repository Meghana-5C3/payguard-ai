import sys
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.api import risk
from backend.app.database import get_db
from backend.app.schemas import TransactionCreateSchema, VerifyChallengeSchema

app = FastAPI(title="PayGuard AI Risk Engine Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk.router)

@app.post("/evaluate")
@app.post("/")
def evaluate_fallback(payload: TransactionCreateSchema, db: Session = Depends(get_db)):
    return risk.evaluate_transaction_risk(payload, db)

@app.post("/verify")
def verify_fallback(payload: VerifyChallengeSchema, db: Session = Depends(get_db)):
    return risk.verify_step_up_challenge(payload, db)
