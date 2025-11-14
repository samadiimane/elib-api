from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies.auth import require_roles
from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserRoleEnum
from app.schemas.user import (
    AdminUserCreate,
    AdminUserOut,
    AdminUsersPage,
    AdminUserToggleActive,
    AdminUserUpdateRoles,
)
from app.services.auth import create_user_with_password, get_user_with_roles, set_user_roles


router = APIRouter(
    prefix="/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_roles(UserRoleEnum.admin))],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users", response_model=AdminUsersPage)
def list_users(
    q: str | None = Query(default=None, description="Case-insensitive email search."),
    role: UserRoleEnum | None = Query(default=None, description="Filter by a specific role."),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> AdminUsersPage:
    filters = []
    email_pattern = _email_pattern(q)
    if email_pattern is not None:
        filters.append(func.lower(User.email).like(email_pattern, escape="\\"))
    if role is not None:
        filters.append(User.roles.any(UserRole.role == role))

    stmt = (
        select(User)
        .options(selectinload(User.roles))
        .order_by(User.created_at.desc())
    )
    if filters:
        stmt = stmt.where(*filters)

    total_stmt = select(func.count()).select_from(User)
    if filters:
        total_stmt = total_stmt.where(*filters)
    total = db.execute(total_stmt).scalar_one()

    offset = (page - 1) * page_size
    result = db.execute(stmt.offset(offset).limit(page_size))
    users = result.scalars().all()
    items = [_serialize_admin_user(user) for user in users]
    return AdminUsersPage(items=items, total=total, page=page, page_size=page_size)


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
) -> AdminUserOut:
    requested_roles = payload.roles if payload.roles is not None else [UserRoleEnum.researcher]
    try:
        user = create_user_with_password(
            db,
            email=payload.email,
            password=payload.password,
            roles=requested_roles,
            is_active=True,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return _load_admin_user(db, user.id)


@router.patch("/users/{user_id}/roles", response_model=AdminUserOut)
def replace_user_roles(
    user_id: int,
    payload: AdminUserUpdateRoles,
    db: Session = Depends(get_db),
) -> AdminUserOut:
    user = _get_user_or_404(db, user_id)
    try:
        set_user_roles(db, user=user, roles=payload.roles)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return _load_admin_user(db, user_id)


@router.patch("/users/{user_id}/active", response_model=AdminUserOut)
def toggle_user_active(
    user_id: int,
    payload: AdminUserToggleActive,
    db: Session = Depends(get_db),
) -> AdminUserOut:
    user = _get_user_or_404(db, user_id)
    user.is_active = payload.is_active
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return _load_admin_user(db, user_id)


def _load_admin_user(db: Session, user_id: int) -> AdminUserOut:
    user = _get_user_or_404(db, user_id)
    return _serialize_admin_user(user)


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = get_user_with_roles(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _serialize_admin_user(user: User) -> AdminUserOut:
    role_values = sorted((_coerce_role_enum(role.role) for role in user.roles), key=lambda role: role.value)
    return AdminUserOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        roles=role_values,
        created_at=user.created_at,
    )


def _coerce_role_enum(value: UserRoleEnum | str) -> UserRoleEnum:
    if isinstance(value, UserRoleEnum):
        return value
    return UserRoleEnum(value)


def _email_pattern(term: str | None) -> str | None:
    if term is None:
        return None
    cleaned = term.strip().lower()
    if not cleaned:
        return None
    escaped = cleaned.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


__all__ = ["router"]
