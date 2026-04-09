# Document upload, listing, and deletion (JWT required; user-scoped access).

from fastapi import APIRouter, Depends

from app.core.security import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/")
def upload_document() -> None:
    """Stub: validate file type/size, persist metadata, enqueue indexing."""
    pass


@router.get("/")
def list_documents() -> None:
    """Stub: return current user's documents."""
    pass


@router.delete("/{document_id}")
def delete_document(document_id: int) -> None:
    """Stub: delete document and related chunks for current user only."""
    pass
