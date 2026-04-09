# SQLAlchemy engine, session factory, declarative Base, and FastAPI DB dependency.

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""

    pass


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield one database session per request (close after response)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
