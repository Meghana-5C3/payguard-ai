import os
import json
from fastapi import APIRouter, HTTPException
from backend.app.schemas import ModelMetricsResponseSchema

router = APIRouter(prefix="/api/v1/metrics", tags=["Model Health & Performance"])

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts"))

@router.get("/performance", response_model=ModelMetricsResponseSchema)
def get_model_metrics():
    metrics_file = os.path.join(ARTIFACTS_DIR, "metrics.json")
    if not os.path.exists(metrics_file):
        raise HTTPException(status_code=404, detail="Model metrics file not found. Train the ML model first.")

    with open(metrics_file, "r") as f:
        metrics_data = json.load(f)

    return metrics_data
