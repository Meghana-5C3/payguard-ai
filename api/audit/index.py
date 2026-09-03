import sys
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.api import audit
from backend.app.database import get_db

app = FastAPI(title="PayGuard AI Audit Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit.router)

@app.get("/logs")
@app.get("/")
def logs_fallback(
    evaluation_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return audit.get_audit_logs(evaluation_id=evaluation_id, limit=limit, db=db)
