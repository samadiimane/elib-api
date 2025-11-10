from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal
from app.models.user import User, UserRoleEnum
from app.services.auth import decode_access_token


_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    """
    Resolve the authenticated user from a JWT access token.

    The returned ORM object is detached from the session so it can be safely
    used in routes without keeping the DB session open.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    session: Session = SessionLocal()
    try:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == int(user_id))
        )
        user = session.execute(stmt).scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # Detach so the object can outlive the session.
        session.expunge(user)
        for role in list(user.roles):
            session.expunge(role)
        return user
    finally:
        session.close()


def require_roles(*roles: UserRoleEnum | str) -> Callable[[User], User]:
    expected_roles = {_coerce_role(role) for role in roles if role}

    def dependency(user: User = Depends(get_current_user)) -> User:
        if not expected_roles:
            return user
        user_roles = {_coerce_role(r.role) for r in user.roles}
        if user_roles.isdisjoint(expected_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


def _coerce_role(role: UserRoleEnum | str) -> UserRoleEnum:
    if isinstance(role, UserRoleEnum):
        return role
    return UserRoleEnum(role)


__all__ = ["get_current_user", "require_roles"]
