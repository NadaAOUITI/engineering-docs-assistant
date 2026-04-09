# User-related request/response shapes (registration, profile).

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Stub: payload for POST /auth/register."""

    email: EmailStr
    password: str
