from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic response envelope for paginated listings."""

    items: Sequence[T]
    total: int
    page: int
    page_size: int
    has_next: bool


__all__ = ["PaginatedResponse"]
