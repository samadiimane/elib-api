from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies.auth import require_roles
from app.models.user import UserRoleEnum


class UserRoleCapabilities(BaseModel):
    add: bool
    remove: bool
    replace: bool


class UsersCapabilities(BaseModel):
    list: bool
    create: bool
    roles: UserRoleCapabilities
    activate: bool


class DocumentCapabilities(BaseModel):
    list: bool
    create: bool
    update: bool
    delete: bool
    restore: bool
    presign: bool


class CategoryCapabilities(BaseModel):
    treeRead: bool
    treeWrite: bool
    reorder: bool
    move: bool


class AuthorCapabilities(BaseModel):
    list: bool
    create: bool
    update: bool
    delete: bool
    softDelete: bool
    restore: bool


class JournalCapabilities(BaseModel):
    list: bool
    create: bool
    update: bool
    softDelete: bool
    restore: bool
    coverPresign: bool


class CollectionCapabilities(BaseModel):
    list: bool
    create: bool
    update: bool
    delete: bool
    assignDocs: bool
    coverPresign: bool


class EventCapabilities(BaseModel):
    list: bool
    create: bool
    update: bool
    delete: bool


class UploadCapabilities(BaseModel):
    presign: bool


class AdminCapabilities(BaseModel):
    users: UsersCapabilities
    documents: DocumentCapabilities
    categories: CategoryCapabilities
    authors: AuthorCapabilities
    journals: JournalCapabilities
    collections: CollectionCapabilities
    events: EventCapabilities
    uploads: UploadCapabilities


DEFAULT_ADMIN_CAPABILITIES = AdminCapabilities(
    users=UsersCapabilities(
        list=True,
        create=True,
        roles=UserRoleCapabilities(add=True, remove=True, replace=True),
        activate=True,
    ),
    documents=DocumentCapabilities(
        list=True,
        create=True,
        update=True,
        delete=True,
        restore=True,
        presign=True,
    ),
    categories=CategoryCapabilities(treeRead=True, treeWrite=True, reorder=True, move=True),
    authors=AuthorCapabilities(list=True, create=True, update=True, delete=True, softDelete=True, restore=True),
    journals=JournalCapabilities(
        list=True,
        create=True,
        update=True,
        softDelete=True,
        restore=True,
        coverPresign=True,
    ),
    collections=CollectionCapabilities(
        list=True,
        create=True,
        update=True,
        delete=True,
        assignDocs=True,
        coverPresign=True,
    ),
    events=EventCapabilities(list=True, create=True, update=True, delete=True),
    uploads=UploadCapabilities(presign=True),
)


router = APIRouter(
    prefix="/v1/admin/capabilities",
    tags=["admin-capabilities"],
    dependencies=[Depends(require_roles(UserRoleEnum.admin, UserRoleEnum.committee))],
)


@router.get("", response_model=AdminCapabilities)
def get_admin_capabilities() -> AdminCapabilities:
    return DEFAULT_ADMIN_CAPABILITIES


__all__ = ["router", "AdminCapabilities", "DEFAULT_ADMIN_CAPABILITIES"]
