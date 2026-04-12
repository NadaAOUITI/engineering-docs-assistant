# Shared pytest fixtures: app TestClient, database session overrides, auth helpers.

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
from app.models.plan import Plan

# Default: Docker Compose service `db-test` (see docker-compose.yml). Override with TEST_DATABASE_URL.
_DEFAULT_TEST_DB_URL = "postgresql+psycopg://app:app@127.0.0.1:5433/engineering_docs_test"


@pytest.fixture(scope="session")
def engine():
    url = os.environ.get("TEST_DATABASE_URL", _DEFAULT_TEST_DB_URL)
    eng = create_engine(url)
    with eng.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    SessionTesting = sessionmaker(bind=connection)
    session = SessionTesting()
    yield session
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def default_plan(db_session):
    plan = Plan(name="free", max_documents=10, max_file_size_mb=10)
    db_session.add(plan)
    db_session.flush()
    return plan


@pytest.fixture(autouse=True)
def upload_dir(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))


@pytest.fixture(autouse=True)
def mock_index_document_delay(monkeypatch):
    monkeypatch.setattr("app.api.documents.index_document.delay", lambda document_id: None)


@pytest.fixture
def client(db_session, default_plan):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
