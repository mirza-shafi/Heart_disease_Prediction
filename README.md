# Heart Disease Prediction — FastAPI + Docker

A simple FastAPI service that serves predictions from a machine-learning classifier
trained on the [Heart Disease dataset](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset)
(UCI Cleveland). It is containerized with Docker and ready to deploy on Render.

> The goal of this project is to demonstrate Docker + deployment, not to maximize accuracy.

## Features / Endpoints

| Method | Path       | Description                                   |
|--------|------------|-----------------------------------------------|
| GET    | `/health`  | Liveness check + whether the model is loaded  |
| GET    | `/info`    | Model type, feature list, target, classes     |
| POST   | `/predict` | Returns `heart_disease: true/false` + probability |
| GET    | `/docs`    | Interactive Swagger UI                         |

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + endpoints
│   └── schemas.py       # Pydantic request/response models
├── data/
│   └── heart.csv        # Training data (303 rows, 13 features + target)
├── model/
│   └── heart_model.joblib   # Trained scikit-learn pipeline
├── train.py             # Trains the model and saves it with joblib
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Input Features

`age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal`

The target is binarized to presence (1) vs absence (0) of heart disease.

The model is a scikit-learn `Pipeline` of `StandardScaler` + `RandomForestClassifier`
(~84% test accuracy).

## Run Locally (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (Optional) retrain the model — a trained model is already included.
python train.py

uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs

## Run with Docker Compose

```bash
docker compose build
docker compose up
```

Then visit http://localhost:8000/docs

Stop with `docker compose down`.

## Example Requests

```bash
# Health
curl http://localhost:8000/health

# Info
curl http://localhost:8000/info

# Predict
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
        "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
        "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1
      }'
```

Sample response:

```json
{ "heart_disease": true, "probability": 0.6804 }
```

## Deploy on Render

1. Push this project to a GitHub repository (see below).
2. In the [Render dashboard](https://dashboard.render.com/), click
   **New → Web Service** and connect your GitHub repo.
3. Configure the service:
   - **Language / Runtime:** `Docker`
   - **Root Directory:** leave blank (the `Dockerfile` is at the repo root)
   - **Instance Type:** Free is sufficient
4. Click **Create Web Service**. Render builds the image from the `Dockerfile`.
   The container listens on the `$PORT` Render injects (the `CMD` already handles this).
5. Once live, test the public URL:

```bash
curl https://<your-service>.onrender.com/health
curl https://<your-service>.onrender.com/info
curl -X POST https://<your-service>.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}'
```

## Push to GitHub

```bash
git init
git add .
git commit -m "Heart Disease Prediction FastAPI + Docker"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Live Deployment URL

> Add your Render URL here after deploying, e.g.
> `https://heart-disease-api.onrender.com`
