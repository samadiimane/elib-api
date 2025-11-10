from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import AuthProvider, UserRoleEnum


class AuthIdentityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: AuthProvider
    provider_user_id: str | None
    created_at: datetime
    updated_at: datetime


class UserRoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: UserRoleEnum


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    identities: list[AuthIdentityOut] = Field(default_factory=list)
    roles: list[UserRoleOut] = Field(default_factory=list)


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(min_length=1)


class RoleRequest(BaseModel):
    role: UserRoleEnum


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class AuthResponse(TokenResponse):
    user: UserOut


__all__ = [
    "AuthIdentityOut",
    "UserRoleOut",
    "UserOut",
    "UserCreateRequest",
    "LoginRequest",
    "GoogleAuthRequest",
    "RoleRequest",
    "TokenResponse",
    "AuthResponse",
]
