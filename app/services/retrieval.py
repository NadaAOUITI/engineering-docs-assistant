# pgvector similarity search and prompt assembly (user_id filter required on every search).

import re
from typing import Any

from groq import Groq
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.chunk import Chunk

_CHUNK_CITE_PATTERN = re.compile(r"\[CHUNK id:\s*(\d+)\]", re.IGNORECASE)


def retrieve_relevant_chunks(
    user_id: int,
    question_embedding: list[float],
    *,
    limit: int = 5,
    db: Session | None = None,
) -> list[dict[str, Any]]:
    """Nearest-neighbor search on Chunk.embedding with mandatory user_id filter."""
    owns_session = db is None
    if owns_session:
        db = SessionLocal()
    try:
        stmt = (
            select(
                Chunk.id,
                Chunk.text,
                Chunk.chunk_index,
                Chunk.document_id,
            )
            .where(Chunk.user_id == user_id)
            .order_by(Chunk.embedding.cosine_distance(question_embedding))
            .limit(limit)
        )
        rows = db.execute(stmt).all()
        return [
            {
                "id": row.id,
                "text": row.text,
                "chunk_index": row.chunk_index,
                "document_id": row.document_id,
            }
            for row in rows
        ]
    finally:
        if owns_session:
            db.close()


def _build_rag_prompt(question: str, retrieved_chunks: list[dict[str, Any]]) -> str:
    context_blocks: list[str] = []
    for chunk in retrieved_chunks:
        context_blocks.append(f"[CHUNK id: {chunk['id']}]\n{chunk['text']}")
    context = "\n\n".join(context_blocks) if context_blocks else "(No relevant document chunks were retrieved.)"

    return (
        "You are an engineering documentation assistant. Answer the question using only the "
        "provided context chunks. When you rely on a chunk, cite it inline using exactly this "
        "format: [CHUNK id: <id>]. Do not invent chunk ids. If the context is insufficient, say "
        "so clearly.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context}"
    )


def _parse_cited_chunk_ids(answer: str, allowed_ids: set[int]) -> list[int]:
    cited: list[int] = []
    seen: set[int] = set()
    for match in _CHUNK_CITE_PATTERN.finditer(answer):
        chunk_id = int(match.group(1))
        if chunk_id in allowed_ids and chunk_id not in seen:
            cited.append(chunk_id)
            seen.add(chunk_id)
    return cited


def answer_with_citations(
    user_id: int,
    question: str,
    retrieved_chunks: list[dict[str, Any]],
) -> tuple[str, list[int]]:
    """Call Groq with labeled chunks; return answer text and cited chunk ids from the response."""
    del user_id  # reserved for future per-user policy hooks; retrieval is already user-scoped

    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured")

    allowed_ids = {int(chunk["id"]) for chunk in retrieved_chunks}
    prompt = _build_rag_prompt(question, retrieved_chunks)

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    answer = (response.choices[0].message.content or "").strip()
    cited_ids = _parse_cited_chunk_ids(answer, allowed_ids)
    return answer, cited_ids
