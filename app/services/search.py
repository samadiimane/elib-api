from __future__ import annotations

from typing import Mapping, Sequence, Tuple

from sqlalchemy.sql import ColumnElement


def ilike_pattern(term: str | None) -> str:
    """Return a sanitized ILIKE pattern for partial matches."""
    if term is None:
        return "%"
    cleaned = term.strip()
    if not cleaned:
        return "%"
    escaped = cleaned.replace("%", r"\%").replace("_", r"\_")
    return f"%{escaped}%"


def validate_sort(
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


def decade_bounds(year: int) -> Tuple[int, int]:
    """Return inclusive decade bounds for a given year."""
    start = year - (year % 10)
    return start, start + 9


# Backwards-compatible aliases
def build_ilike_pattern(term: str) -> str:
    return ilike_pattern(term)


def resolve_sort_key(
    sort: str | None,
    *,
    allowed: Mapping[str, ColumnElement],
    default: str,
) -> ColumnElement:
    return validate_sort(sort, allowed=allowed, default=default)
