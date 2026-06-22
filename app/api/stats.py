from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi_cache.decorator import cache

from app.db.database import get_db
from app.db.models import Prediction
from app.schemas import StatsSummary

router = APIRouter()

@router.get("/summary", response_model=StatsSummary)
@cache(expire=60)
def get_stats_summary(db: Session = Depends(get_db)):
    total = db.query(Prediction).count()
    if total == 0:
        return StatsSummary(
            total_predictions=0,
            percent_positive=0.0,
            percent_negative=0.0,
            avg_probability=0.0
        )
    
    positives = db.query(Prediction).filter(Prediction.heart_disease == True).count()
    avg_prob = db.query(func.avg(Prediction.probability)).scalar()
    
    return StatsSummary(
        total_predictions=total,
        percent_positive=round((positives / total) * 100, 2),
        percent_negative=round(((total - positives) / total) * 100, 2),
        avg_probability=round(float(avg_prob or 0.0), 4)
    )
