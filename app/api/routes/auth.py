from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_roles
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User, UserRoleEnum
from app.schemas.user import (
    AuthResponse,
    GoogleAuthRequest,
    LoginRequest,
    RoleRequest,
    UserCreateRequest,
    UserOut,
)
from app.services.auth import (
    assign_role,
    authenticate_user,
    create_access_token,
    create_user_with_password,
    ensure_google_user,
    get_user_with_roles,
    remove_role,
    validate_google_id_token,
)


router = APIRouter(prefix="/v1/auth", tags=["auth"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
) -> UserOut:
    try:
        user = create_user_with_password(db, email=payload.email, password=payload.password)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return _load_user_as_schema(db, user.id)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    normalized_email = payload.email.strip().lower()
    user = authenticate_user(db, email=normalized_email, password=payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    return _build_auth_response(user)


@router.post("/google", response_model=AuthResponse)
def login_with_google(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    try:
        profile = validate_google_id_token(payload.id_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    try:
        user = ensure_google_user(
            db,
            email=profile["email"],
            provider_user_id=profile["sub"],
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    return _build_auth_response(user)


@router.get("/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    return _load_user_as_schema(db, current_user.id)


@router.post(
    "/users/{user_id}/roles",
    response_model=UserOut,
    dependencies=[Depends(require_roles(UserRoleEnum.admin))],
)
def add_role(
    user_id: int,
    payload: RoleRequest,
    db: Session = Depends(get_db),
) -> UserOut:
    user = _get_user_or_404(db, user_id)
    assign_role(db, user=user, role=payload.role)
    return _load_user_as_schema(db, user_id)


@router.delete(
    "/users/{user_id}/roles/{role}",
    response_model=UserOut,
    dependencies=[Depends(require_roles(UserRoleEnum.admin))],
)
def remove_role_route(
    user_id: int,
    role: UserRoleEnum,
    db: Session = Depends(get_db),
) -> UserOut:
    user = _get_user_or_404(db, user_id)
    removed = remove_role(db, user=user, role=role)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not assigned")
    return _load_user_as_schema(db, user_id)


def _build_auth_response(user: User) -> AuthResponse:
    token = create_access_token(user=user)
    expires_in = settings.access_token_exp_minutes * 60
    user_out = UserOut.model_validate(user)
    return AuthResponse(
        access_token=token,
        expires_in=expires_in,
        user=user_out,
    )


def _load_user_as_schema(db: Session, user_id: int) -> UserOut:
    user = get_user_with_roles(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(user)


def _get_user_or_404(db: Session, user_id: int) -> User:
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
