# Engineering Docs Research Assistant

RAG-oriented backend: engineers upload PDF/Markdown/text, documents are chunked and embedded, and questions return answers with citations.

## Stack

- Python 3.12, FastAPI, SQLAlchemy, Celery, Redis  
- PostgreSQL 16 with pgvector for vector(768) embeddings  
- JWT auth (python-jose, passlib)  
- Groq for the LLM; sentence-transformers runs locally for embeddings  

## Layout

- app/ — API routers, core config/security/database, ORM models, Pydantic schemas, services, Celery tasks  
- docs/adr/ — architecture decision records  
- tests/ — pytest suite (to be expanded)  

## Configuration

Copy .env.example to .env and set secrets (especially JWT_SECRET_KEY and GROQ_API_KEY). See app/core/config.py for variable names.

## Run with Docker

```bash
docker compose up --build
```

API: http://localhost:8000. PostgreSQL and Redis are exposed on 5432 and 6379 for local clients.

The API and worker share one image; Compose overrides the command for the Celery worker.

## Development (without Docker)

Create a virtualenv, install dependencies from requirements.txt, run PostgreSQL with pgvector and Redis, set DATABASE_URL / REDIS_URL, then:

```bash
uvicorn app.main:app --reload
```

Celery (optional for local indexing):

```bash
celery -A app.worker.tasks:celery_app worker -l info
```

## Note

Milestone 1 is structure and stubs only: authentication, ingestion, retrieval, and persistence logic are implemented in later milestones. Enable the vector extension in PostgreSQL before using embedding columns in production.
