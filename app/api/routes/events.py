from __future__ import annotations

import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.event import EVENT_TYPES, Event
from app.repositories.events import EventRepository, serialize_winners
from app.schemas.event import (
    AwardDetailsOut,
    AwardWinnerOut,
    EventBaseOut,
    EventDetailOut,
    ExhibitionDetailsOut,
    SeminarAgendaItemOut,
    SeminarDetailsOut,
    SeminarSpeakerOut,
)
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/v1/events", tags=["events"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _load_json(value, default):
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError, ValueError):
            return default
    return default


def _serialize_event_detail(event: Event) -> EventDetailOut:
    base = EventBaseOut.model_validate(event)
    details = None

    if event.type == "seminar":
        payload = event.seminar_detail
        if payload is not None:
            speakers_raw = _load_json(getattr(payload, "speakers_json", None), [])
            agenda_raw = _load_json(getattr(payload, "agenda_json", None), [])
            media_raw = _load_json(getattr(payload, "media_json", None), [])

            speakers = []
            for item in speakers_raw:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                if not name:
                    continue
                speakers.append(
                    SeminarSpeakerOut(
                        name=name,
                        role=item.get("role"),
                        affiliation=item.get("affiliation"),
                    )
                )

            agenda = []
            for item in agenda_raw:
                if not isinstance(item, dict):
                    continue
                title = item.get("title")
                if not title:
                    continue
                agenda.append(
                    SeminarAgendaItemOut(
                        title=title,
                        time=item.get("time"),
                        speaker=item.get("speaker"),
                    )
                )

            media = [entry for entry in media_raw if isinstance(entry, str)]

            details = SeminarDetailsOut(
                speakers=speakers,
                agenda=agenda,
                media=media,
            )
        else:
            details = None
    elif event.type == "award":
        payload = event.award_detail
        winners = [
            AwardWinnerOut(**winner_dict)
            for winner_dict in serialize_winners(event.award_winners or [])
        ]
        if payload is not None or winners:
            details = AwardDetailsOut(
                award_year=getattr(payload, "award_year", None) if payload is not None else None,
                discipline=getattr(payload, "discipline", None) if payload is not None else None,
                notes=getattr(payload, "notes", None) if payload is not None else None,
                winners=winners,
            )
        else:
            details = None
    elif event.type == "exhibition":
        payload = event.exhibition_detail
        if payload is not None:
            gallery_raw = _load_json(getattr(payload, "gallery_json", None), [])
            gallery = [entry for entry in gallery_raw if isinstance(entry, str)]
            details = ExhibitionDetailsOut(
                venue=getattr(payload, "venue", None),
                curator=getattr(payload, "curator", None),
                gallery=gallery,
            )
        else:
            details = None

    return EventDetailOut(
        **base.model_dump(),
        body=event.body,
        details=details,
    )


@router.get("", response_model=PaginatedResponse[EventBaseOut])
def list_events(
    type: Literal["seminar", "award", "exhibition"] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[EventBaseOut]:
    repo = EventRepository(db)
    items, total = repo.list(event_type=type, page=page, page_size=page_size)
    payload = [EventBaseOut.model_validate(event) for event in items]
    has_next = (page * page_size) < (total or 0)
    return PaginatedResponse[EventBaseOut](
        items=payload,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
    )


@router.get("/{slug}", response_model=EventDetailOut)
def get_event(slug: str, db: Session = Depends(get_db)) -> EventDetailOut:
    repo = EventRepository(db)
    event = repo.get_by_slug(slug)
    if event is None or not event.is_published:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.type not in EVENT_TYPES:
        raise HTTPException(status_code=500, detail="Unsupported event type")
    return _serialize_event_detail(event)
