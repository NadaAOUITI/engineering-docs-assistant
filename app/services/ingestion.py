# Parse uploads, split text, compute embeddings, and persist chunks (invoked by worker).

import io
from pathlib import Path

from pypdf import PdfReader

from app.core.config import settings


def document_storage_path(user_id: int, document_id: int, file_type: str) -> Path:
    return Path(settings.upload_dir) / str(user_id) / f"{document_id}.{file_type}"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")
    if not text:
        return []
    step = chunk_size - overlap
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start += step
    return chunks


def extract_text(file_type: str, content: bytes) -> str:
    ft = file_type.lower().lstrip(".")
    if ft in ("md", "txt"):
        return content.decode("utf-8", errors="replace")
    if ft == "pdf":
        reader = PdfReader(io.BytesIO(content))
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    raise ValueError(f"Unsupported file type: {file_type}")
