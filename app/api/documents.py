# Document upload, listing, and deletion (JWT required; user-scoped access).

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.plan import Plan
from app.models.user import User
from app.schemas.document import DocumentRead
from app.services.ingestion import document_storage_path
from app.worker.tasks import index_document

router = APIRouter()

ALLOWED_TYPES = frozenset({"pdf", "md", "txt"})


@router.post("/", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    filename = file.filename or ""
    if "." not in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    content = await file.read()
    size_mb = len(content) / (1024**2)

    plan = db.get(Plan, current_user.plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Plan not found",
        )
    if size_mb > plan.max_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large",
        )

    doc_count = db.scalar(
        select(func.count()).select_from(Document).where(Document.user_id == current_user.id)
    )
    if doc_count is not None and doc_count >= plan.max_documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document limit reached",
        )

    document = Document(
        user_id=current_user.id,
        filename=filename,
        file_type=ext,
        status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    path = document_storage_path(current_user.id, document.id, ext)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_bytes(content)
    except OSError:
        db.delete(document)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store file",
        ) from None

    index_document.delay(document.id)
    return document


@router.get("/", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    document = db.get(Document, document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    path = document_storage_path(document.user_id, document.id, document.file_type)
    db.execute(
        delete(Chunk).where(
            Chunk.document_id == document.id,
            Chunk.user_id == current_user.id,
        )
    )
    db.delete(document)
    db.commit()

    if path.exists():
        path.unlink()
