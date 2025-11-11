from __future__ import annotations

from typing import Generator, Iterable

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies.auth import require_roles
from app.db.session import SessionLocal
from app.models.user import User, UserRoleEnum
from app.schemas.user import UserOut


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


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)) -> list[UserOut]:
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.identities))
        .order_by(User.created_at.desc())
    )
    users: Iterable[User] = db.scalars(stmt).all()
    if not users:
        return []
    return [UserOut.model_validate(user) for user in users]


__all__ = ["router"]
