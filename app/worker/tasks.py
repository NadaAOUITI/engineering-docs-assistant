# Celery tasks for async document chunking, embedding, and pgvector upserts.

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "engineering_docs",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@celery_app.task
def index_document(document_id: int) -> None:
    """Stub: load document, chunk, embed with sentence-transformers, insert Chunk rows."""
    raise NotImplementedError
