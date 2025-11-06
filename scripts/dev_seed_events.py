"""Seed exemplar events for seminars, awards, and exhibitions."""

from __future__ import annotations

from datetime import date
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

from app.db.session import SessionLocal
from app.models.event import (
    AwardEvent,
    AwardWinner,
    Event,
    ExhibitionEvent,
    SeminarEvent,
)

configure_mappers()


def _get_event(session, slug: str) -> Event | None:
    stmt = select(Event).where(Event.slug == slug)
    return session.execute(stmt).scalar_one_or_none()


def _upsert_event(session, slug: str, **kwargs) -> Event:
    event = _get_event(session, slug)
    if event is None:
        event = Event(slug=slug, **kwargs)
        session.add(event)
    else:
        for key, value in kwargs.items():
            setattr(event, key, value)
    session.flush()
    return event


def seed_events() -> None:
    session = SessionLocal()
    try:
        seminar = _upsert_event(
            session,
            "digitisation-labs-open-seminar",
            type="seminar",
            title="Digitisation Labs Open Seminar",
            summary="Tour the Foundation's preservation lab with live demonstrations.",
            body=(
                "The seminar introduces the Foundation's conservation workflows for fragile periodicals. "
                "Speakers will outline capture pipelines and metadata standards in use across the archive."
            ),
            start_date=date(2025, 2, 18),
            end_date=date(2025, 2, 18),
            location="Tangier Conservation Studio",
            cover_image_url="https://example.org/images/events/seminar-labs.jpg",
            order_index=1,
        )
        seminar_detail = seminar.seminar_detail or SeminarEvent(event_id=seminar.id)
        seminar_detail.speakers_json = [
            {"name": "Dr. Hind Alami", "role": "Lead Conservator", "affiliation": "AKT Research Foundation"},
            {"name": "Karim Ben Salah", "role": "Metadata Analyst"},
        ]
        seminar_detail.agenda_json = [
            {"time": "09:30", "title": "Welcome & overview", "speaker": "Dr. Hind Alami"},
            {"time": "10:15", "title": "Digitisation walkthrough", "speaker": "Karim Ben Salah"},
            {"time": "11:00", "title": "Open Q&A"},
        ]
        seminar_detail.media_json = [
            "https://example.org/images/events/seminar-labs-gallery-1.jpg",
            "https://example.org/images/events/seminar-labs-gallery-2.jpg",
        ]
        seminar.seminar_detail = seminar_detail

        workshop = _upsert_event(
            session,
            "oral-history-recording-workshop",
            type="seminar",
            title="Oral History Recording Workshop",
            summary="Hands-on training for capturing oral testimonies.",
            body="Participants will work in pairs to prepare equipment, conduct interviews, and catalogue recordings.",
            start_date=date(2025, 4, 12),
            end_date=date(2025, 4, 12),
            location="Foundation Studio B",
            cover_image_url="https://example.org/images/events/seminar-oral-history.jpg",
            order_index=2,
        )
        workshop_detail = workshop.seminar_detail or SeminarEvent(event_id=workshop.id)
        workshop_detail.speakers_json = [
            {"name": "Samira El Haddad", "role": "Archivist"},
            {"name": "Prof. Omar Rahmouni", "role": "Historian"},
        ]
        workshop_detail.agenda_json = [
            {"time": "10:00", "title": "Interview ethics briefing"},
            {"time": "11:30", "title": "Hands-on equipment lab"},
            {"time": "14:00", "title": "Cataloguing workshop"},
        ]
        workshop_detail.media_json = []
        workshop.seminar_detail = workshop_detail

        award = _upsert_event(
            session,
            "heritage-research-awards-2025",
            type="award",
            title="Heritage Research Awards 2025",
            summary="Recognising innovative research that unlocks regional archives.",
            body="The annual awards champion original scholarship and collaborative archival practices.",
            start_date=date(2025, 6, 20),
            location="Great Hall, AKT Foundation",
            cover_image_url="https://example.org/images/events/awards-2025.jpg",
            order_index=3,
        )
        award_detail = award.award_detail or AwardEvent(event_id=award.id)
        award_detail.award_year = 2025
        award_detail.discipline = "Archival Science"
        award_detail.notes = "Panel chaired by Dr. Leila Fassi."
        award.award_detail = award_detail
        award.award_winners.clear()
        award.award_winners.extend(
            [
                AwardWinner(
                    rank=1,
                    winner_name="Amal Idrissi",
                    work_title="Digitising the Tangier Municipal Archives",
                    affiliation="University of Rabat",
                ),
                AwardWinner(
                    rank=2,
                    winner_name="Youssef Kadiri",
                    work_title="The Medina Soundscapes Project",
                    affiliation="Independent Researcher",
                ),
                AwardWinner(
                    rank=3,
                    winner_name="Lina Ben Omar",
                    work_title="Mapping Seaside Exhibitions 1920-1950",
                    affiliation="AKT Research Fellows",
                ),
            ]
        )

        exhibition = _upsert_event(
            session,
            "documentary-exhibition-lights-of-tangier",
            type="exhibition",
            title="Lights of Tangier",
            summary="An exhibition of restored documentary photography from 1890-1940.",
            body=(
                "The exhibition traces the evolution of documentary photography in Tangier, "
                "highlighting restoration techniques and newly digitised negatives."
            ),
            start_date=date(2025, 9, 5),
            end_date=date(2025, 10, 18),
            location="AKT Gallery Wing",
            cover_image_url="https://example.org/images/events/exhibition-lights.jpg",
            order_index=4,
        )
        exhibition_detail = exhibition.exhibition_detail or ExhibitionEvent(event_id=exhibition.id)
        exhibition_detail.venue = "Gallery Wing A"
        exhibition_detail.curator = "Nadia Benkirane"
        exhibition_detail.gallery_json = [
            "https://example.org/images/events/exhibition-lights-gallery-1.jpg",
            "https://example.org/images/events/exhibition-lights-gallery-2.jpg",
        ]
        exhibition.exhibition_detail = exhibition_detail

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed_events()
    print("Seeded events & activities.")
