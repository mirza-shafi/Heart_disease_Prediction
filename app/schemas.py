"""Pydantic schemas for request and response payloads."""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Any
from datetime import datetime
import uuid

class HeartFeatures(BaseModel):
    """Input features for a single heart-disease prediction."""
    age: int = Field(..., ge=0, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="Sex (1 = male, 0 = female)")
    cp: int = Field(..., ge=0, le=3, description="Chest pain type (0-3)")
    trestbps: float = Field(..., ge=0, description="Resting blood pressure (mm Hg)")
    chol: float = Field(..., ge=0, description="Serum cholesterol (mg/dl)")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl (1/0)")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG results (0-2)")
    thalach: float = Field(..., ge=0, description="Maximum heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise-induced angina (1/0)")
    oldpeak: float = Field(..., description="ST depression induced by exercise")
    slope: int = Field(..., ge=0, le=2, description="Slope of the peak exercise ST segment (0-2)")
    ca: int = Field(..., ge=0, le=4, description="Number of major vessels colored by fluoroscopy (0-4)")
    thal: int = Field(..., ge=0, le=3, description="Thalassemia (0-3)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
                "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
                "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1,
            }
        }
    }

class PredictionResponse(BaseModel):
    prediction_id: uuid.UUID
    heart_disease: bool
    probability: float
    risk_level: str
    confidence: str
    recommendation: str
    timestamp: datetime
    model_version: str

class BatchPredictionRequest(BaseModel):
    patients: List[HeartFeatures]

class BatchPredictionResponse(BaseModel):
    task_id: str
    message: str = "Batch prediction task enqueued"

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class InfoResponse(BaseModel):
    model_type: str
    features: list[str]
    n_features: int
    target: str
    classes: dict[str, str]
    accuracy: float
    f1_score: float

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FeedbackCreate(BaseModel):
    is_correct: bool
    comments: Optional[str] = None

class ExplanationResponse(BaseModel):
    base_value: float
    shap_values: list[float]
    feature_names: list[str]
    features_input: dict[str, Any]

class StatsSummary(BaseModel):
    total_predictions: int
    percent_positive: float
    percent_negative: float
    avg_probability: float

