from __future__ import annotations

from datetime import date
from typing import Literal, Optional, Sequence, Union

from pydantic import BaseModel, ConfigDict


class EventBaseOut(BaseModel):
    """Shared event attributes for listings."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    type: Literal["seminar", "award", "exhibition"]
    title: str
    summary: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None
    cover_image_url: Optional[str] = None


class SeminarSpeakerOut(BaseModel):
    name: str
    role: Optional[str] = None
    affiliation: Optional[str] = None


class SeminarAgendaItemOut(BaseModel):
    title: str
    time: Optional[str] = None
    speaker: Optional[str] = None


class SeminarDetailsOut(BaseModel):
    kind: Literal["seminar"] = "seminar"
    speakers: Sequence[SeminarSpeakerOut] = ()
    agenda: Sequence[SeminarAgendaItemOut] = ()
    media: Sequence[str] = ()


class AwardWinnerOut(BaseModel):
    id: int
    rank: Optional[int] = None
    winner_name: str
    work_title: Optional[str] = None
    affiliation: Optional[str] = None
    notes: Optional[str] = None


class AwardDetailsOut(BaseModel):
    kind: Literal["award"] = "award"
    award_year: Optional[int] = None
    discipline: Optional[str] = None
    notes: Optional[str] = None
    winners: Sequence[AwardWinnerOut] = ()


class ExhibitionDetailsOut(BaseModel):
    kind: Literal["exhibition"] = "exhibition"
    venue: Optional[str] = None
    curator: Optional[str] = None
    gallery: Sequence[str] = ()


EventDetailsOut = Union[SeminarDetailsOut, AwardDetailsOut, ExhibitionDetailsOut]


class EventDetailOut(EventBaseOut):
    """Detailed representation of an event."""

    body: Optional[str] = None
    details: Optional[EventDetailsOut] = None


__all__ = [
    "EventBaseOut",
    "EventDetailOut",
    "SeminarDetailsOut",
    "AwardDetailsOut",
    "ExhibitionDetailsOut",
    "SeminarSpeakerOut",
    "SeminarAgendaItemOut",
    "AwardWinnerOut",
    "EventDetailsOut",
]
