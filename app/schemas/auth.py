# Auth token and login request shapes.

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Stub: JWT access token returned from POST /auth/login."""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Stub: credentials for POST /auth/login."""

    email: EmailStr
    password: str
