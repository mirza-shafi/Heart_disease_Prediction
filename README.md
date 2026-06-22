# Heart Disease Prediction API (Upgraded)

An upgraded, production-ready FastAPI service that provides machine-learning predictions and explanations for heart disease presence based on clinical features.

**🔗 Live demo:** [https://heartdisease.mirzashafi.com](https://heartdisease.mirzashafi.com)  
**Swagger UI Docs:** [https://heartdisease.mirzashafi.com/docs](https://heartdisease.mirzashafi.com/docs)

---

## 🚀 Upgraded Features

* **Relational Database Integration:** Persistent storage for user records, predictions, and clinical feedback using PostgreSQL (SQLAlchemy ORM).
* **Automated Migrations:** Database schemas are managed via Alembic and applied automatically on application startup.
* **Authentication & Authorization:** Secure endpoints (like history and feedback submission) using JWT (JSON Web Tokens) with a clean JSON registration/login payload.
* **Explainability (SHAP):** Real-time prediction explanations using SHAP values showing feature importance for the Random Forest classifier.
* **Asynchronous Processing:** Long-running batch predictions enqueued via Celery and Redis to prevent blocking the main event loop.
* **Caching & Rate Limiting:** Endpoint response caching (via Redis & `fastapi-cache2`) and rate limiting (via `slowapi` to protect against spam).
* **Structured JSON Logging:** Production-ready JSON logging for easy debugging and monitoring.
* **Automated Pytest Suite:** End-to-end integration tests using a local SQLite configuration.

---

## 🛠️ API Endpoints

### Authentication
* `POST /auth/register` - Register a new user (JSON body).
* `POST /auth/login` - Obtain a JWT Bearer token (JSON body).

### Predictions & Explainability
* `POST /predict` - Single patient prediction (returns risk, confidence, recommendations; saves to DB). *Rate-limited to 10 requests/min.*
* `POST /batch_predict` - Asynchronously predict a list of patients (enqueues a Celery task, returns `task_id`).
* `POST /explain` - Interpret feature contributions using SHAP values.
* `GET /predict/history` - Retrieve prediction history for the authenticated user (requires JWT).
* `POST /feedback/{prediction_id}` - Submit clinical feedback (correct/incorrect) for a prediction (requires JWT).

### Metrics & Metadata
* `GET /model/info` - Expose model metadata (n_features, parameters, accuracy, f1 score).
* `GET /stats/summary` - Aggregate predictions (total count, positive/negative rates, avg probability). *Cached for 60 seconds.*
* `GET /health` - Liveness check and model load status.

---

## 📁 Project Structure

```text
.
├── app/
│   ├── api/             # API Routers (auth, predictions, explain, stats, model)
│   ├── core/            # Configuration, logging, and JWT security setup
│   ├── db/              # SQLAlchemy database setup, models, and session management
│   ├── services/        # ML model loading (SHAP TreeExplainer, predictions)
│   ├── main.py          # FastAPI application initialization & lifespan
│   ├── schemas.py       # Pydantic request/response validation models
│   └── worker.py        # Celery worker tasks
├── alembic/             # Alembic database migration scripts
├── data/                # Heart disease dataset
├── model/               # Serialized ML model and training metrics JSON
├── tests/               # Pytest suite (integration & end-to-end checks)
├── Dockerfile           # Multi-stage production Docker image
├── docker-compose.yml   # Multi-container local orchestration (App, Worker, Postgres, Redis)
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Python dependencies
└── README.md
```

---

## ⚙️ Environment Variables

The application can be configured using a `.env` file or environment variables:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `DATABASE_URL` | `postgresql://user:password@localhost/db` | PostgreSQL connection string (Supabase/Neon/Local) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching connection string |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Redis broker URL for Celery |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Redis result backend for Celery |
| `SECRET_KEY` | `YOUR_SUPER_SECRET_KEY` | Key to encrypt JWT access tokens |
| `ALGORITHM` | `HS256` | JWT signing algorithm |

---

## 🏃 Run Locally

### Using Docker Compose (Recommended)
This spins up the FastAPI app, Celery worker, PostgreSQL, and Redis in a single command:
```bash
docker-compose up --build
```
Access the interactive docs at: [http://localhost:8000/docs](http://localhost:8000/docs).

### Without Docker
1. **Set up virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Setup environment:**
   Copy `.env.example` to `.env` and fill in your connection strings (e.g. Supabase Postgres & Redis).
3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```
4. **Start the API:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 🧪 Run Tests

We use a local SQLite configuration to run tests with zero dependencies:
```bash
DATABASE_URL="sqlite:///./test_temp.db" PYTHONPATH=. .venv/bin/pytest tests/ -vv
```

---

## ☁️ Deploying to Render

1. **Deploy Databases:**
   * Create a **PostgreSQL** database on Render (or use Supabase/Neon). Copy the connection URI.
   * Create a **Redis** instance on Render (or use Upstash). Copy the connection URI.
2. **Deploy the FastAPI Web Service:**
   * Create a new **Web Service** on Render.
   * Connect your GitHub repository.
   * Choose **Docker** as the runtime.
   * Add the following **Environment Variables**:
     * `DATABASE_URL` = `[Your PostgreSQL connection string]`
     * `REDIS_URL` = `[Your Redis connection string]`
     * `CELERY_BROKER_URL` = `[Your Redis connection string/1]`
     * `CELERY_RESULT_BACKEND` = `[Your Redis connection string/2]`
     * `SECRET_KEY` = `[Your custom random string]`
3. **Launch:** Render will build the Docker container and start serving the API!
