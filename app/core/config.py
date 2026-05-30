# Environment-backed settings (database URL, JWT, Redis, Groq, embedding model).

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://app:app@localhost:5432/engineering_docs"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2"
    upload_dir: str = "uploads"


settings = Settings()
