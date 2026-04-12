# Celery tasks for async document chunking, embedding, and pgvector upserts.

from celery import Celery
from sentence_transformers import SentenceTransformer
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Document
from app.services.ingestion import chunk_text, document_storage_path, extract_text

celery_app = Celery(
    "engineering_docs",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.embedding_model_name)
    return _embedding_model


@celery_app.task
def index_document(document_id: int) -> None:
    db: Session = SessionLocal()
    try:
        document = db.get(Document, document_id)
        if document is None:
            return

        document.status = "processing"
        db.commit()

        path = document_storage_path(document.user_id, document.id, document.file_type)
        content = path.read_bytes()
        text = extract_text(document.file_type, content)
        texts = chunk_text(text)

        db.execute(
            delete(Chunk).where(
                Chunk.document_id == document.id,
                Chunk.user_id == document.user_id,
            )
        )

        if texts:
            model = _get_embedding_model()
            embeddings = model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            for i, segment in enumerate(texts):
                db.add(
                    Chunk(
                        document_id=document.id,
                        user_id=document.user_id,
                        text=segment,
                        embedding=embeddings[i].tolist(),
                        chunk_index=i,
                    )
                )

        document.status = "indexed"
        db.commit()
    except Exception:
        db.rollback()
        document = db.get(Document, document_id)
        if document is not None:
            document.status = "failed"
            db.commit()
        raise
    finally:
        db.close()
