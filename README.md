# Engineering Docs Research Assistant

This repository is a multi-user FastAPI backend for asking questions over uploaded engineering documents (PDF, Markdown, or plain text). It targets engineers who want citations grounded in their own files rather than a generic model, and it is built without LangChain or other RAG frameworks so every step of the pipeline stays visible and accountable.

## Architecture

Three flows split the work by latency and responsibility. Upload is synchronous: the client sends a file, FastAPI validates type and size against the user’s plan, writes the document row and bytes to disk, and returns immediately with a pending status. Indexing is asynchronous: FastAPI only enqueues a Celery task; a worker loads the file, extracts text, chunks it, runs sentence-transformers, and writes chunk rows with embeddings into PostgreSQL. That split avoids holding an HTTP connection open while a large PDF is parsed and embedded, which can take tens of seconds; the tradeoff is operational complexity (Redis, a worker process, and status fields on the document) instead of a single process. The query path is designed to stay on the FastAPI side: embedding the question, pgvector similarity search, assembling context, and calling the LLM would all run in the API process, not in Celery, because the user is waiting for one answer and the expensive part is bounded by retrieval width, not full-corpus indexing.

## API

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /auth/register | — | Create a new user account |
| POST | /auth/login | — | Authenticate and receive a JWT |
| POST | /documents | ✓ | Upload a document (PDF, MD, TXT) |
| GET | /documents | ✓ | List your uploaded documents |
| DELETE | /documents/{id} | ✓ | Delete a document and its chunks |
| POST | /queries | ✓ | Ask a question, get a cited answer |
| GET | /queries | ✓ | Fetch your query history |
| DELETE | /queries/{id} | ✓ | Delete a query from history |

## Security model

API-level checks (JWT, ownership on document IDs) are necessary but not sufficient. If similarity search ever ran without scoping vectors to the authenticated user, a bug or mistaken query could return another tenant’s chunks because pgvector only sees vectors, not business rules. The rule used here is to filter every nearest-neighbor query by user_id in SQL, the same place the vectors live, so isolation is enforced where the data is read, not only where routes are declared. That duplicates the user id in chunk rows and adds an index predicate on every search, which is extra storage and query structure in exchange for a smaller blast radius if application code regresses.

## Running locally

```bash
git clone https://github.com/NadaAOUITI/engineering-docs-assistant
cd engineering-docs-assistant
cp .env.example .env
docker compose up
```

## Tech stack

The service runs on Python 3.12 with FastAPI. PostgreSQL holds users, plans, documents, chunks, and query history, with the pgvector extension for 768-dimensional vector columns. Redis backs Celery as broker and result backend. Embeddings use sentence-transformers locally; the configured chat model is called through the Groq HTTP API. Docker Compose brings up the database, Redis, the API, and a Celery worker from the same image.

## Decisions

Architecture notes live under docs/adr/. ADR 001 records why embeddings stay in PostgreSQL with pgvector instead of a separate vector database: for this scale, one transactional store keeps chunk rows and metadata consistent and avoids synchronizing a second system, at the cost of giving up Qdrant’s specialized scaling and operational tooling.
