import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.api import public_predict
from backend.app.schemas import PublicPredictionRequestSchema

app = FastAPI(title="PayGuard AI Public Prediction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_predict.router)

@app.post("/predict")
@app.post("/")
def predict_fallback(payload: PublicPredictionRequestSchema):
    return public_predict.predict_public_transaction(payload)
