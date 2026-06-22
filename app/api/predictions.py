import uuid
from typing import List
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi_cache.decorator import cache
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.db.models import User, Prediction, Feedback
from app.api.deps import get_current_user_optional, get_current_user
from app.schemas import (
    HeartFeatures, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse, FeedbackCreate
)
from app.services.model_service import model_service
from app.services.ml import determine_risk_level, determine_confidence, get_recommendation
from app.core.config import settings
from app.worker import batch_predict_task

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/predict", response_model=PredictionResponse)
@limiter.limit("10/minute")
def predict(
    request: Request,
    features: HeartFeatures, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user_optional)
):
    df = pd.DataFrame([features.model_dump()])
    X = df[model_service.features]
    
    pred, proba = model_service.predict(X)
    probability = float(proba[0])
    heart_disease = bool(pred[0])
    
    risk_level = determine_risk_level(probability)
    confidence = determine_confidence(probability)
    recommendation = get_recommendation(risk_level)
    
    # Save to db
    db_prediction = Prediction(
        user_id=current_user.id if current_user else None,
        **features.model_dump(),
        heart_disease=heart_disease,
        probability=probability,
        risk_level=risk_level,
        confidence=confidence,
        recommendation=recommendation,
        model_version=settings.VERSION
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return PredictionResponse(
        prediction_id=db_prediction.id,
        heart_disease=heart_disease,
        probability=probability,
        risk_level=risk_level,
        confidence=confidence,
        recommendation=recommendation,
        timestamp=db_prediction.timestamp,
        model_version=settings.VERSION
    )

@router.post("/batch_predict", response_model=BatchPredictionResponse)
def batch_predict(
    request: BatchPredictionRequest,
    current_user: User = Depends(get_current_user_optional)
):
    patients_data = [p.model_dump() for p in request.patients]
    user_id = current_user.id if current_user else None
    
    task = batch_predict_task.delay(patients_data, user_id)
    return BatchPredictionResponse(task_id=task.id)

@router.get("/predict/history", response_model=List[PredictionResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.timestamp.desc()).all()
    # Pydantic will auto map fields for PredictionResponse
    # but we need to ensure prediction_id maps to id
    responses = []
    for p in predictions:
        responses.append(PredictionResponse(
            prediction_id=p.id,
            heart_disease=p.heart_disease,
            probability=p.probability,
            risk_level=p.risk_level,
            confidence=p.confidence,
            recommendation=p.recommendation,
            timestamp=p.timestamp,
            model_version=p.model_version
        ))
    return responses

@router.post("/feedback/{prediction_id}")
def submit_feedback(
    prediction_id: uuid.UUID,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id, Prediction.user_id == current_user.id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found or not owned by user")
    
    existing_feedback = db.query(Feedback).filter(Feedback.prediction_id == prediction_id).first()
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this prediction")
        
    db_feedback = Feedback(
        prediction_id=prediction_id,
        user_id=current_user.id,
        is_correct=feedback.is_correct,
        comments=feedback.comments
    )
    db.add(db_feedback)
    db.commit()
    return {"message": "Feedback submitted successfully"}
