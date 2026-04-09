# Password hashing, JWT creation/validation, and FastAPI user dependency.

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Stub: verify a plaintext password against a stored hash."""
    raise NotImplementedError


def get_password_hash(password: str) -> str:
    """Stub: hash a password for storage."""
    raise NotImplementedError


def create_access_token(subject: dict[str, Any]) -> str:
    """Stub: encode a JWT with configured secret and expiry."""
    raise NotImplementedError


def decode_access_token(token: str) -> dict[str, Any]:
    """Stub: decode and validate JWT; raise on invalid/expired token."""
    raise NotImplementedError


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
) -> dict[str, Any]:
    """Stub: require Bearer JWT; return user identity or raise 401 (all other routes use this)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented",
    )
