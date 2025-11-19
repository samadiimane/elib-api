from __future__ import annotations

from datetime import datetime
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryKind
from app.schemas.pagination import PaginatedResponse


class CategoryNodeOut(BaseModel):
    id: int
    name: str
    slug: str
    kind: CategoryKind
    parent_id: int | None
    order: int = Field(serialization_alias="order")
    document_count: int | None = None
    children: list["CategoryNodeOut"] | None = None


class CategoryPathFragment(BaseModel):
    id: int
    slug: str
    name: str


class CategoryListItemOut(BaseModel):
    id: int
    name: str
    slug: str
    kind: CategoryKind
    parent_id: int | None
    order: int
    path: Sequence[CategoryPathFragment]
    document_count: int
    created_at: datetime


class CategoryListResponse(PaginatedResponse[CategoryListItemOut]):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class CategoryCreate(BaseModel):
    name: str
    slug: str | None = None
    kind: CategoryKind
    parent_id: int | None = None
    order: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class CategoryMoveRequest(BaseModel):
    parent_id: int | None = None
    order: int | None = None


class ReorderItem(BaseModel):
    id: int
    order: int


class CategoryReorderRequest(BaseModel):
    parent_id: int | None = None
    items: list[ReorderItem]


__all__ = [
    "CategoryNodeOut",
    "CategoryListItemOut",
    "CategoryListResponse",
    "CategoryPathFragment",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryMoveRequest",
    "CategoryReorderRequest",
    "ReorderItem",
]
