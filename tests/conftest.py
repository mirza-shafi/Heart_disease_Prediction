import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db, engine, SessionLocal
from app.core.config import settings
from app.worker import celery_app

# Configure Celery in eager mode for testing
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True
)

@pytest.fixture(scope="session")
def db_engine():
    # Run database migrations to set up schema for testing
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield engine
    
    # Clean up file-based SQLite database if used
    import os
    if settings.DATABASE_URL.startswith("sqlite:///"):
        db_file = settings.DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_file) and db_file not in ("", ":memory:"):
            try:
                os.remove(db_file)
            except Exception:
                pass

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
