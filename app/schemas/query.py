# Query submission and history shapes.

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QueryCreate(BaseModel):
    question: str = Field(..., min_length=1)


class QueryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    answer: str
    cited_chunk_ids: list[int]
    created_at: datetime
