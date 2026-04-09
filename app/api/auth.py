# Public auth routes: user registration and login (no JWT on these paths).

from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
def register() -> None:
    """Stub: create user and assign plan."""
    pass


@router.post("/login")
def login() -> None:
    """Stub: return JWT access token."""
    pass
