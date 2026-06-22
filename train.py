"""Train a Heart Disease classifier and save it with joblib.

Usage:
    python train.py
"""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_ORDER = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]
TARGET = "target"

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "heart.csv"
MODEL_DIR = ROOT / "model"
MODEL_PATH = MODEL_DIR / "heart_model.joblib"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    # Strip any stray BOM/whitespace from column names.
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]

    X = df[FEATURE_ORDER]
    y = (df[TARGET] > 0).astype(int)  # binary: presence (1) vs absence (0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=200, max_depth=6, random_state=42
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    print(f"Test accuracy: {acc:.4f}")
    print(f"Test F1 Score: {f1:.4f}")
    print(classification_report(y_test, preds, target_names=["absence", "presence"]))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")
    
    metrics_path = MODEL_DIR / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump({"accuracy": acc, "f1_score": f1}, f, indent=2)
    print(f"Saved metrics to {metrics_path}")


if __name__ == "__main__":
    main()
