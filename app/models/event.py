from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

EVENT_TYPES: tuple[str, ...] = ("seminar", "award", "exhibition")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=func.true())
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    seminar_detail: Mapped[Optional["SeminarEvent"]] = relationship(
        "SeminarEvent",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )
    award_detail: Mapped[Optional["AwardEvent"]] = relationship(
        "AwardEvent",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )
    exhibition_detail: Mapped[Optional["ExhibitionEvent"]] = relationship(
        "ExhibitionEvent",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )
    award_winners: Mapped[List["AwardWinner"]] = relationship(
        "AwardWinner",
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="AwardWinner.rank",
    )


class SeminarEvent(Base):
    __tablename__ = "seminar_events"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    speakers_json: Mapped[Optional[list[dict]]] = mapped_column(JSON, nullable=True)
    agenda_json: Mapped[Optional[list[dict]]] = mapped_column(JSON, nullable=True)
    media_json: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    event: Mapped[Event] = relationship("Event", back_populates="seminar_detail")


class AwardEvent(Base):
    __tablename__ = "award_events"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    award_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    discipline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    event: Mapped[Event] = relationship("Event", back_populates="award_detail")


class ExhibitionEvent(Base):
    __tablename__ = "exhibition_events"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gallery_json: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    curator: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    event: Mapped[Event] = relationship("Event", back_populates="exhibition_detail")


class AwardWinner(Base):
    __tablename__ = "award_event_winners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    winner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    work_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    affiliation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    event: Mapped[Event] = relationship("Event", back_populates="award_winners")


__all__ = [
    "EVENT_TYPES",
    "Event",
    "SeminarEvent",
    "AwardEvent",
    "ExhibitionEvent",
    "AwardWinner",
]
