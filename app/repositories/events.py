from __future__ import annotations

from typing import Optional, Sequence, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import Session, selectinload

from app.models.event import Event, AwardWinner


class EventRepository:
    """Data-access helpers for events and activities."""

    def __init__(self, session: Session):
        self._session = session

    def list(
        self,
        *,
        event_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list[Event], int]:
        page = max(page, 1)
        page_size = max(min(page_size, 100), 1)
        offset = (page - 1) * page_size

        filters = [Event.is_published.is_(True)]
        if event_type:
            filters.append(Event.type == event_type)

        ordered_stmt = (
            sa.select(Event)
            .where(*filters)
            .order_by(
                Event.order_index.asc(),
                Event.start_date.desc(),
                Event.created_at.desc(),
            )
        )
        items_stmt = ordered_stmt.offset(offset).limit(page_size)
        count_stmt = sa.select(sa.func.count()).select_from(Event).where(*filters)

        items = self._session.execute(items_stmt).scalars().unique().all()
        total = self._session.execute(count_stmt).scalar_one()

        return items, total

    def get_by_slug(self, slug: str) -> Event | None:
        stmt = (
            sa.select(Event)
            .where(Event.slug == slug)
            .options(
                selectinload(Event.seminar_detail),
                selectinload(Event.award_detail),
                selectinload(Event.exhibition_detail),
                selectinload(Event.award_winners),
            )
        )
        return self._session.execute(stmt).scalar_one_or_none()


def serialize_winners(winners: Sequence[AwardWinner]) -> list[dict]:
    ordered = sorted(
        winners,
        key=lambda winner: ((winner.rank if winner.rank is not None else 0), winner.id),
    )
    return [
        {
            "id": winner.id,
            "rank": winner.rank,
            "winner_name": winner.winner_name,
            "work_title": winner.work_title,
            "affiliation": winner.affiliation,
            "notes": winner.notes,
        }
        for winner in ordered
    ]


__all__ = ["EventRepository", "serialize_winners"]
