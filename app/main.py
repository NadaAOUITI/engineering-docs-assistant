# FastAPI application entry: app instance and API router registration.

from fastapi import FastAPI

from app.api import auth, documents, queries

app = FastAPI(title="Engineering Docs Research Assistant")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(queries.router, prefix="/queries", tags=["queries"])
