from __future__ import annotations

from typing import Mapping

from sqlalchemy.sql import ColumnElement


def build_ilike_pattern(term: str) -> str:
    """Return a sanitized ILIKE pattern for partial matches."""
    cleaned = term.strip()
    if not cleaned:
        return "%"
    escaped = cleaned.replace("%", r"\%").replace("_", r"\_")
    return f"%{escaped}%"


def resolve_sort_key(
    sort: str | None,
    *,
    allowed: Mapping[str, ColumnElement],
    default: str,
) -> ColumnElement:
    """Validate and resolve a client-provided sort key to a SQLAlchemy column clause."""
    key = (sort or default).strip().lower()
    if not key:
        key = default
    clause = allowed.get(key)
    if clause is None:
        raise ValueError(f"Unsupported sort key: {sort}")
    return clause
