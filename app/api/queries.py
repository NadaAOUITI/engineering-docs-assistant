# RAG query submission and history (JWT required; user-scoped access).

from fastapi import APIRouter, Depends, HTTPException, status
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.query import Query
from app.models.user import User
from app.schemas.query import QueryCreate, QueryRead
from app.services.retrieval import answer_with_citations

router = APIRouter(dependencies=[Depends(get_current_user)])

_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.embedding_model_name)
    return _embedding_model


def _embed_question(question: str) -> list[float]:
    model = _get_embedding_model()
    vector = model.encode(
        question,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vector.tolist()


@router.post("/", response_model=QueryRead, status_code=status.HTTP_201_CREATED)
def create_query(
    body: QueryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Query:
    question = body.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty",
        )

    question_embedding = _embed_question(question)

    try:
        answer, cited_ids = answer_with_citations(
            current_user.id,
            question,
            question_embedding,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    query = Query(
        user_id=current_user.id,
        question=question,
        answer=answer,
        cited_chunk_ids=cited_ids,
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


@router.get("/", response_model=list[QueryRead])
def list_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Query]:
    stmt = (
        select(Query)
        .where(Query.user_id == current_user.id)
        .order_by(Query.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_query(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    query = db.scalar(
        select(Query).where(
            Query.id == query_id,
            Query.user_id == current_user.id,
        )
    )
    if query is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(query)
    db.commit()
