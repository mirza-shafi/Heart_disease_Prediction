import pandas as pd
from fastapi import APIRouter
from app.schemas import HeartFeatures, ExplanationResponse
from app.services.model_service import model_service

router = APIRouter()

@router.post("/explain", response_model=ExplanationResponse)
def explain_prediction(features: HeartFeatures):
    df = pd.DataFrame([features.model_dump()])
    X = df[model_service.features]
    
    explanation = model_service.explain(X)
    
    return ExplanationResponse(
        base_value=explanation["base_value"],
        shap_values=explanation["shap_values"][0],
        feature_names=model_service.features,
        features_input=features.model_dump()
    )
