# Document list item and upload response shapes.

from datetime import datetime

from pydantic import BaseModel


class DocumentRead(BaseModel):
    """Stub: single document row returned to the client."""

    id: int
    filename: str
    file_type: str
    status: str
    created_at: datetime
