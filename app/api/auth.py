# Public auth routes: user registration and login (no JWT on these paths).

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.plan import Plan
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate

router = APIRouter()


def _default_plan(db: Session) -> Plan:
    plan = db.scalars(select(Plan).order_by(Plan.id).limit(1)).first()
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No subscription plan configured",
        )
    return plan


@router.post("/register", response_model=Token)
def register(body: UserCreate, db: Session = Depends(get_db)) -> Token:
    plan = _default_plan(db)
    email = str(body.email).lower()
    user = User(
        email=email,
        hashed_password=get_password_hash(body.password),
        plan_id=plan.id,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> Token:
    email = str(body.email).lower()
    user = db.scalars(select(User).where(User.email == email)).first()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")
