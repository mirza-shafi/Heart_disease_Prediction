import os
from celery import Celery
import pandas as pd
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Prediction
from app.services.model_service import model_service
from app.services.ml import determine_risk_level, determine_confidence, get_recommendation

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task(name="batch_predict_task")
def batch_predict_task(patients: list[dict], user_id: int = None):
    db = SessionLocal()
    try:
        # We can optimize this by doing a single batch prediction if model_service supports it
        # Actually, model_service.predict takes a DataFrame, so it does support batch
        df = pd.DataFrame(patients)
        
        # Keep only the features expected by the model
        X = df[model_service.features]
        
        preds, probas = model_service.predict(X)
        
        predictions_to_insert = []
        for i, (pred, proba) in enumerate(zip(preds, probas)):
            patient = patients[i]
            probability = float(proba)
            heart_disease = bool(pred)
            
            risk_level = determine_risk_level(probability)
            confidence = determine_confidence(probability)
            recommendation = get_recommendation(risk_level)
            
            db_prediction = Prediction(
                user_id=user_id,
                age=patient["age"],
                sex=patient["sex"],
                cp=patient["cp"],
                trestbps=patient["trestbps"],
                chol=patient["chol"],
                fbs=patient["fbs"],
                restecg=patient["restecg"],
                thalach=patient["thalach"],
                exang=patient["exang"],
                oldpeak=patient["oldpeak"],
                slope=patient["slope"],
                ca=patient["ca"],
                thal=patient["thal"],
                heart_disease=heart_disease,
                probability=probability,
                risk_level=risk_level,
                confidence=confidence,
                recommendation=recommendation,
                model_version=settings.VERSION
            )
            predictions_to_insert.append(db_prediction)
        
        db.add_all(predictions_to_insert)
        db.commit()
        return {"status": "completed", "processed": len(patients)}
    except Exception as e:
        db.rollback()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
