import joblib
import json
from pathlib import Path
import shap
import pandas as pd
from app.core.logger import logger

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "model" / "heart_model.joblib"
METRICS_PATH = Path(__file__).resolve().parent.parent.parent / "model" / "metrics.json"

class ModelService:
    def __init__(self):
        self.model = None
        self.explainer = None
        self.metrics = {"accuracy": 0.0, "f1_score": 0.0}
        self.features = [
            "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"
        ]
        self.load_model()

    def load_model(self):
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
                logger.info(f"Loaded model from {MODEL_PATH}")
                
                # Setup SHAP explainer
                # We need the RandomForestClassifier from the Pipeline to explain it
                # The pipeline steps are typically [('scaler', StandardScaler), ('clf', RandomForestClassifier)]
                if hasattr(self.model, 'named_steps') and 'clf' in self.model.named_steps:
                    clf = self.model.named_steps['clf']
                    self.explainer = shap.TreeExplainer(clf)
                    logger.info("SHAP explainer initialized.")
                else:
                    logger.warning("Could not find 'clf' in model pipeline to initialize SHAP explainer.")
            except Exception as e:
                logger.error(f"Error loading model: {e}")

        if METRICS_PATH.exists():
            try:
                with open(METRICS_PATH, "r") as f:
                    self.metrics = json.load(f)
                logger.info(f"Loaded metrics from {METRICS_PATH}")
            except Exception as e:
                logger.error(f"Error loading metrics: {e}")

    def predict(self, df: pd.DataFrame):
        if not self.model:
            raise ValueError("Model is not loaded")
        pred = self.model.predict(df)
        try:
            proba = self.model.predict_proba(df)[:, 1]
        except (AttributeError, IndexError):
            proba = pred.astype(float)
        return pred, proba

    def explain(self, df: pd.DataFrame):
        if not self.explainer:
            raise ValueError("SHAP explainer is not initialized")
        
        # Transform the features before SHAP explanation since explainer was trained on scaled data
        if hasattr(self.model, 'named_steps') and 'scaler' in self.model.named_steps:
            scaler = self.model.named_steps['scaler']
            X_scaled = scaler.transform(df)
        else:
            X_scaled = df
        
        shap_values = self.explainer.shap_values(X_scaled)
        
        import numpy as np
        
        # TreeExplainer for binary classification might return a list of arrays (one for each class)
        # or a 3D numpy array of shape (num_samples, num_features, num_classes)
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]
        elif isinstance(shap_values, np.ndarray):
            if shap_values.ndim == 3 and shap_values.shape[2] == 2:
                shap_values = shap_values[:, :, 1]
        
        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, tuple, np.ndarray)):
            if len(base_value) == 2:
                base_value = base_value[1]
            elif len(base_value) == 1:
                base_value = base_value[0]
                
        if isinstance(base_value, np.ndarray):
            base_value = base_value.item()
        
        return {
            "base_value": float(base_value) if base_value is not None else 0.0,
            "shap_values": shap_values.tolist()
        }

model_service = ModelService()
