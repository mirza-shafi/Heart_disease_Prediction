"""FastAPI application serving Heart Disease predictions."""
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from app.schemas import (
    HealthResponse,
    HeartFeatures,
    InfoResponse,
    PredictionResponse,
)

# Feature order must match the order used during training.
FEATURE_ORDER = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]

MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "heart_model.joblib"

app = FastAPI(
    title="Heart Disease Prediction API",
    description="Predicts the presence of heart disease from clinical features.",
    version="1.0.0",
)

# Load the model once at startup.
_model = None
if MODEL_PATH.exists():
    _model = joblib.load(MODEL_PATH)


@app.get("/", tags=["root"])
def root():
    return {"message": "Heart Disease Prediction API. See /docs for usage."}


@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
def health():
    return HealthResponse(status="ok", model_loaded=_model is not None)


@app.get("/info", response_model=InfoResponse, tags=["monitoring"])
def info():
    model_type = type(_model).__name__ if _model is not None else "not loaded"
    return InfoResponse(
        model_type=model_type,
        features=FEATURE_ORDER,
        n_features=len(FEATURE_ORDER),
        target="heart_disease",
        classes={"0": "absence", "1": "presence"},
    )


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(features: HeartFeatures):
    if _model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    row = features.model_dump()
    X = pd.DataFrame([[row[name] for name in FEATURE_ORDER]], columns=FEATURE_ORDER)

    pred = int(_model.predict(X)[0])
    try:
        proba = float(_model.predict_proba(X)[0][1])
    except (AttributeError, IndexError):
        proba = float(pred)

    return PredictionResponse(heart_disease=bool(pred), probability=round(proba, 4))
