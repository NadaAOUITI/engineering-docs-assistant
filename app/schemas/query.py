# Query submission and history shapes.

from datetime import datetime

from pydantic import BaseModel


class QueryCreate(BaseModel):
    """Stub: body for POST /queries."""

    question: str


class QueryRead(BaseModel):
    """Stub: stored query with answer and citations."""

    id: int
    question: str
    answer: str
    cited_chunk_ids: list[int]
    created_at: datetime
