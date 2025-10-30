from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryKind


class LinkedJournal(BaseModel):
    """Minimal representation for a journal linked to a category."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str


class CategoryOut(BaseModel):
    """Serialized category representation for listings and detail."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    kind: CategoryKind
    parent_id: int | None
    description: str | None
    linked_journal: LinkedJournal | None = Field(default=None, validation_alias="journal")


class CategoryCounts(BaseModel):
    """Aggregate counters for a category."""

    documents: int


class CategoryChildOut(BaseModel):
    """Serialized representation for a child category listing."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    kind: CategoryKind
    description: str | None = None
    counts: CategoryCounts | None = None


class CategoryChildrenResponse(BaseModel):
    """Envelope for category children listings."""

    items: list[CategoryChildOut]


class CategoryDetailOut(BaseModel):
    """Category detail payload including aggregated counts."""

    category: CategoryOut
    counts: CategoryCounts


__all__ = [
    "CategoryOut",
    "CategoryCounts",
    "CategoryChildOut",
    "CategoryChildrenResponse",
    "CategoryDetailOut",
    "LinkedJournal",
]
