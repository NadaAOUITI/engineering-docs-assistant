# RAG query submission and history (JWT required; user-scoped access).

from fastapi import APIRouter, Depends

from app.core.security import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/")
def create_query() -> None:
    """Stub: retrieve chunks, call LLM, persist query with citations."""
    pass


@router.get("/")
def list_queries() -> None:
    """Stub: return current user's past queries."""
    pass


@router.delete("/{query_id}")
def delete_query(query_id: int) -> None:
    """Stub: delete query row for current user only."""
    pass
