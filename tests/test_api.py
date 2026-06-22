import pytest
from app.db.models import Prediction

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_info(client):
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "model_type" in data
    assert data["target"] == "heart_disease"

def test_predict(client):
    payload = {
        "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
        "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction_id" in data
    assert "heart_disease" in data
    assert "probability" in data
    assert "risk_level" in data
    assert "recommendation" in data

def test_register_and_login(client):
    # Register
    reg_response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert reg_response.status_code == 200
    assert reg_response.json()["username"] == "testuser"
    
    # Login
    login_response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_predict_explain(client):
    payload = {
        "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
        "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "shap_values" in data
    assert "base_value" in data

def test_stats_summary(client):
    response = client.get("/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "percent_positive" in data
    assert "percent_negative" in data
    assert "avg_probability" in data

def test_batch_predict(client, db_session):
    initial_count = db_session.query(Prediction).count()
    
    payload = {
        "patients": [
            {
                "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
                "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
                "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1
            },
            {
                "age": 50, "sex": 0, "cp": 2, "trestbps": 130, "chol": 200,
                "fbs": 0, "restecg": 1, "thalach": 160, "exang": 1,
                "oldpeak": 1.0, "slope": 1, "ca": 1, "thal": 2
            }
        ]
    }
    response = client.post("/batch_predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    
    final_count = db_session.query(Prediction).count()
    assert final_count == initial_count + 2
