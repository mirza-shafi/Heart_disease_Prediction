from fastapi import APIRouter
from app.schemas import InfoResponse
from app.services.model_service import model_service

router = APIRouter()

@router.get("/info", response_model=InfoResponse)
def get_model_info():
    model_type = type(model_service.model).__name__ if model_service.model is not None else "not loaded"
    if hasattr(model_service.model, 'named_steps') and 'clf' in model_service.model.named_steps:
        model_type = type(model_service.model.named_steps['clf']).__name__

    return InfoResponse(
        model_type=model_type,
        features=model_service.features,
        n_features=len(model_service.features),
        target="heart_disease",
        classes={"0": "absence", "1": "presence"},
        accuracy=model_service.metrics.get("accuracy", 0.0),
        f1_score=model_service.metrics.get("f1_score", 0.0)
    )
