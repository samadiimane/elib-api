from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.category import CategoryKind


class CategoryOut(BaseModel):
    """Serialized category representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int | None
    kind: CategoryKind
    slug: str
    name: str
    description: str | None


__all__ = ["CategoryOut"]
