from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AuthorOut(BaseModel):
    """Lightweight author representation for document responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name_ar: str
    full_name_lat: str | None = None
    affiliation: str | None = None


__all__ = ["AuthorOut"]
