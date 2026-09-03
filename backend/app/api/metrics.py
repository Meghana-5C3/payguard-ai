import os
import json
from fastapi import APIRouter, HTTPException
from backend.app.schemas import ModelMetricsResponseSchema

router = APIRouter(prefix="/api/v1/metrics", tags=["Model Health & Performance"])

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts"))

@router.get("/performance", response_model=ModelMetricsResponseSchema)
def get_model_metrics():
    possible_paths = [
        os.path.join(ARTIFACTS_DIR, "metrics.json"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts", "metrics.json")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app", "ml", "artifacts", "metrics.json")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts", "model_metrics.json")),
        "/var/task/backend/app/ml/artifacts/metrics.json",
    ]
    target_path = None
    for p in possible_paths:
        if p and os.path.exists(p):
            target_path = p
            break

    if not target_path:
        raise HTTPException(status_code=404, detail="Model metrics file not found.")

    with open(target_path, "r") as f:
        metrics_data = json.load(f)

    return metrics_data
