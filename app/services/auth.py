from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.user import AuthIdentity, AuthProvider, User, UserRole, UserRoleEnum


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_BCRYPT_MAX_BYTES = 72
ACCESS_TOKEN_ALGORITHM = "HS256"


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def _truncate_for_bcrypt(password: str) -> str:
    # bcrypt works on bytes, so we truncate on bytes, not on characters
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) <= _BCRYPT_MAX_BYTES:
        return password
    # cut the bytes then decode back
    pw_bytes = pw_bytes[:_BCRYPT_MAX_BYTES]
    return pw_bytes.decode("utf-8", errors="ignore")

def hash_password(password: str) -> str:
    """
    Hash passwords with bcrypt and sensible defaults.
    Always truncate to 72 bytes because bcrypt ignores anything after that.
    """
    safe_pw = _truncate_for_bcrypt(password)
    return _pwd_context.hash(safe_pw)

def verify_password(password: str, password_hash: str | None) -> bool:
    """
    Compare a plaintext password to a stored hash.
    Must apply the same truncation strategy as hash_password.
    """
    if not password_hash:
        return False
    safe_pw = _truncate_for_bcrypt(password)
    return _pwd_context.verify(safe_pw, password_hash)


# ---------------------------------------------------------------------------
# User creation and lookup
# ---------------------------------------------------------------------------

def get_user_by_email(session: Session, email: str) -> User | None:
    """Fetch a user by normalized email."""
    normalized = email.strip().lower()
    if not normalized:
        return None
    stmt = select(User).where(User.email == normalized)
    return session.execute(stmt).scalar_one_or_none()


def get_user_with_roles(session: Session, user_id: int) -> User | None:
    """Retrieve a user and eagerly load role relationships."""
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles), selectinload(User.identities))
    )
    return session.execute(stmt).scalar_one_or_none()


def create_user_with_password(
    session: Session,
    *,
    email: str,
    password: str,
    roles: Iterable[UserRoleEnum | str] | None = None,
    is_active: bool = True,
) -> User:
    """Create a new user and attach the password identity atomically."""
    normalized_email = email.strip().lower()
    if not normalized_email:
        raise ValueError("email must not be empty")

    existing = get_user_by_email(session, normalized_email)
    if existing is not None:
        raise ValueError("A user with this email already exists")

    requested_roles = _unique_roles(_normalize_roles(roles) or [UserRoleEnum.researcher])
    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        is_active=is_active,
    )
    user.identities.append(
        AuthIdentity(
            provider=AuthProvider.password,
            provider_user_id=None,
        )
    )
    for role in requested_roles:
        user.roles.append(UserRole(role=role))

    session.add(user)
    try:
        session.flush()
    except IntegrityError as exc:
        # Re-raise with a clearer error for the API layer
        raise ValueError("Failed to create user record") from exc
    return user


def ensure_google_user(
    session: Session,
    *,
    email: str,
    provider_user_id: str,
) -> User:
    """
    Find or create a user tied to a Google identity.

    Users created through Google receive the default 'researcher' role.
    """
    normalized_email = email.strip().lower()
    if not normalized_email:
        raise ValueError("email must not be empty")

    normalized_provider_id = provider_user_id.strip()
    if not normalized_provider_id:
        raise ValueError("provider_user_id must not be empty")

    user = (
        session.execute(
            select(User)
            .where(User.email == normalized_email)
            .options(selectinload(User.roles), selectinload(User.identities))
        ).scalar_one_or_none()
    )

    if user is None:
        user = User(
            email=normalized_email,
            is_active=True,
        )
        user.roles.append(UserRole(role=UserRoleEnum.researcher))
        session.add(user)
        session.flush()  # ensure user.id before linking identity
    else:
        # Ensure roles and identities loaded for downstream use
        _ = user.roles  # noqa: F841
        _ = user.identities  # noqa: F841

    link_google_identity(
        session,
        user=user,
        provider_user_id=normalized_provider_id,
    )
    session.flush()
    return user


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def authenticate_user(session: Session, *, email: str, password: str) -> User | None:
    """Validate credentials and return the user if they are active."""
    stmt = (
        select(User)
        .where(User.email == email.strip().lower())
        .options(selectinload(User.roles), selectinload(User.identities))
    )
    user = session.execute(stmt).scalar_one_or_none()
    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        return None
    return user


def create_access_token(
    *,
    user: User,
    expires_minutes: int | None = None,
) -> str:
    """Create a signed JWT access token for the given user."""
    expires_minutes = expires_minutes or settings.access_token_exp_minutes
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "roles": _user_role_values(user),
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=ACCESS_TOKEN_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.auth_secret,
            algorithms=[ACCESS_TOKEN_ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid or expired token") from exc
    return payload


def validate_google_id_token(id_token: str) -> dict[str, str]:
    """
    Placeholder Google token validation.

    Accepts a JSON string containing at least ``sub`` and ``email``. This keeps
    the flow testable while the real Google verification is implemented.
    """
    try:
        data = json.loads(id_token)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid Google token payload") from exc

    if not isinstance(data, dict):
        raise ValueError("Invalid Google token payload")

    subject = str(data.get("sub", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    if not subject or not email:
        raise ValueError("Google token missing required fields")

    return {"sub": subject, "email": email}


# ---------------------------------------------------------------------------
# Identity + role helpers
# ---------------------------------------------------------------------------

def link_google_identity(
    session: Session,
    *,
    user: User,
    provider_user_id: str,
) -> AuthIdentity:
    """Attach a Google identity to an existing user (idempotent)."""
    normalized_id = provider_user_id.strip()
    if not normalized_id:
        raise ValueError("provider_user_id must not be empty")

    existing = session.execute(
        select(AuthIdentity).where(
            AuthIdentity.provider == AuthProvider.google,
            AuthIdentity.provider_user_id == normalized_id,
        )
    ).scalar_one_or_none()

    if existing is not None:
        if existing.user_id != user.id:
            raise ValueError("Google account already linked to another user")
        return existing

    identity = AuthIdentity(
        provider=AuthProvider.google,
        provider_user_id=normalized_id,
    )
    user.identities.append(identity)
    session.add(identity)
    session.flush()
    return identity


def assign_role(
    session: Session,
    *,
    user: User,
    role: UserRoleEnum | str,
) -> UserRole:
    """Ensure a role is attached to the user."""
    role_enum = _coerce_role(role)
    existing = session.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role == role_enum,
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    user_role = UserRole(role=role_enum)
    user.roles.append(user_role)
    session.add(user_role)
    session.flush()
    return user_role


def remove_role(
    session: Session,
    *,
    user: User,
    role: UserRoleEnum | str,
) -> bool:
    """Remove a specific role from a user if present."""
    role_enum = _coerce_role(role)
    user_role = session.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role == role_enum,
        )
    ).scalar_one_or_none()
    if user_role is None:
        return False

    session.delete(user_role)
    session.flush()
    return True


def _normalize_roles(
    roles: Iterable[UserRoleEnum | str] | None,
) -> list[UserRoleEnum]:
    if not roles:
        return []
    return [_coerce_role(role) for role in roles]


def _unique_roles(roles: Iterable[UserRoleEnum]) -> list[UserRoleEnum]:
    seen: set[UserRoleEnum] = set()
    unique: list[UserRoleEnum] = []
    for role in roles:
        if role not in seen:
            seen.add(role)
            unique.append(role)
    return unique


def _coerce_role(role: UserRoleEnum | str) -> UserRoleEnum:
    if isinstance(role, UserRoleEnum):
        return role
    return UserRoleEnum(role)


def _user_role_values(user: User) -> list[str]:
    return [
        role.role.value if isinstance(role.role, UserRoleEnum) else str(role.role)
        for role in user.roles
    ]


__all__ = [
    "ACCESS_TOKEN_ALGORITHM",
    "assign_role",
    "authenticate_user",
    "create_access_token",
    "create_user_with_password",
    "decode_access_token",
    "ensure_google_user",
    "get_user_by_email",
    "get_user_with_roles",
    "hash_password",
    "link_google_identity",
    "remove_role",
    "validate_google_id_token",
    "verify_password",
]
