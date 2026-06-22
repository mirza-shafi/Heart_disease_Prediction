from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logger import logger
from app.db.database import engine, Base
from app.api.predictions import limiter
from app.api import auth, predictions, explain, stats, model
from app.schemas import HealthResponse
from app.services.model_service import model_service

# Note: In a production app, use Alembic for migrations instead of create_all
# Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    
    # Run database migrations on startup
    try:
        logger.info("Running database migrations via Alembic...")
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")
    except Exception as e:
        logger.error(f"Error running database migrations: {e}")

    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    logger.info("Shutting down FastAPI application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Predicts the presence of heart disease from clinical features.",
    version=settings.VERSION,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(predictions.router, tags=["prediction"])
app.include_router(explain.router, tags=["explain"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(model.router, prefix="/model", tags=["model"])

@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
def health():
    return HealthResponse(status="ok", model_loaded=model_service.model is not None)
