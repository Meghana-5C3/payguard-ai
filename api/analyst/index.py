import sys
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.api import analyst
from backend.app.database import get_db
from backend.app.schemas import AnalystOverrideSchema

app = FastAPI(title="PayGuard AI Analyst Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyst.router)

@app.get("/queue")
@app.get("/")
def queue_fallback(status_filter: str = "ALL", db: Session = Depends(get_db)):
    return analyst.get_analyst_queue(status_filter, db)

@app.post("/override")
def override_fallback(payload: AnalystOverrideSchema, db: Session = Depends(get_db)):
    return analyst.submit_analyst_override(payload, db)
