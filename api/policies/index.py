import sys
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.api import policies
from backend.app.database import get_db
from backend.app.schemas import PolicyRuleCreateSchema

app = FastAPI(title="PayGuard AI Policy Engine Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(policies.router)

@app.get("/")
def get_policies_fallback(db: Session = Depends(get_db)):
    return policies.list_policies(db=db)

@app.post("/reset-defaults")
def reset_defaults_fallback(db: Session = Depends(get_db)):
    return policies.reset_default_policies(db=db)

@app.put("/{rule_id}")
def update_policy_fallback(rule_id: str, payload: PolicyRuleCreateSchema, db: Session = Depends(get_db)):
    return policies.update_policy(rule_id=rule_id, payload=payload, db=db)
