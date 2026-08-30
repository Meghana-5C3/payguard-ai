from fastapi import APIRouter, HTTPException, status
from backend.app.schemas import PublicPredictionRequestSchema, PublicPredictionResponseSchema
from backend.app.ml.public_inference import public_inference_service

router = APIRouter(prefix="/api/public", tags=["Public Benchmark Inference"])

@router.post("/predict", response_model=PublicPredictionResponseSchema, summary="Evaluate Public Fraud Benchmark Transaction")
def predict_public_transaction(payload: PublicPredictionRequestSchema):
    """
    Executes transaction fraud prediction on the frozen Public Benchmark Pipeline (Kaggle creditcard.csv PCA features).
    
    Guarantees:
    - Performs prediction using frozen XGBoost model, preprocessor, and isotonic calibrator.
    - Zero training or refitting occurs.
    - Preserves native feature names (Time, V1..V28, Amount).
    - Threshold is fixed at 0.5.
    """
    try:
        data_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        include_explanations = data_dict.pop("include_explanations", False)
        result = public_inference_service.predict(data_dict, include_explanations=include_explanations)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Public benchmark inference failed: {str(e)}")
