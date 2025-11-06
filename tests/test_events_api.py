from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.routes import events as events_routes
from app.main import app
from app.models.event import (
    AwardEvent,
    AwardWinner,
    Event,
    ExhibitionEvent,
    SeminarEvent,
)


def _override_db(SessionLocal):
    def dependency():
        with SessionLocal() as session:
            yield session

    return dependency


def test_list_events_filters_by_type(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        seminar = Event(
            slug="spring-conservation-seminar",
            type="seminar",
            title="Spring Conservation Seminar",
            summary="Focus on restoration practices.",
            start_date=date(2025, 3, 20),
            is_published=True,
        )
        session.add(seminar)
        session.flush()
        session.add(
            SeminarEvent(
                event_id=seminar.id,
                speakers_json=[
                    {"name": "Dr. Hind Alami", "role": "Keynote"},
                ],
            )
        )

        award = Event(
            slug="annual-research-awards",
            type="award",
            title="Annual Research Awards",
            summary="Celebrating outstanding scholarship.",
            start_date=date(2025, 5, 1),
            is_published=True,
        )
        session.add(award)
        session.flush()
        session.add(AwardEvent(event_id=award.id, award_year=2025, discipline="Digital Humanities"))
        session.add_all(
            [
                AwardWinner(event_id=award.id, rank=1, winner_name="Amal Idrissi"),
                AwardWinner(event_id=award.id, rank=2, winner_name="Karim Ben Salah"),
            ]
        )

        unpublished = Event(
            slug="upcoming-exhibition",
            type="exhibition",
            title="Unpublished Exhibition",
            is_published=False,
        )
        session.add(unpublished)

    app.dependency_overrides[events_routes.get_db] = _override_db(SessionLocal)
    try:
        client = TestClient(app)
        response = client.get("/v1/events", params={"type": "seminar"})
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["slug"] == "spring-conservation-seminar"

        response_all = client.get("/v1/events")
        assert response_all.status_code == 200, response_all.text
        all_payload = response_all.json()
        # unpublished event should be filtered automatically
        assert all_payload["total"] == 2
        returned_slugs = {item["slug"] for item in all_payload["items"]}
        assert returned_slugs == {"spring-conservation-seminar", "annual-research-awards"}
    finally:
        app.dependency_overrides.pop(events_routes.get_db, None)


def test_event_detail_includes_type_specific_data(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        exhibition = Event(
            slug="documentary-media-week",
            type="exhibition",
            title="Documentary Media Week",
            summary="A week of screenings and talks.",
            body="Daily screenings from the archive.",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 7),
            location="Tangier Cultural Center",
            cover_image_url="https://example.org/media/week.jpg",
            is_published=True,
        )
        session.add(exhibition)
        session.flush()
        session.add(
            ExhibitionEvent(
                event_id=exhibition.id,
                venue="Main Gallery",
                curator="Samira El Haddad",
                gallery_json=[
                    "https://example.org/media/gallery1.jpg",
                    "https://example.org/media/gallery2.jpg",
                ],
            )
        )

    app.dependency_overrides[events_routes.get_db] = _override_db(SessionLocal)
    try:
        client = TestClient(app)
        response = client.get("/v1/events/documentary-media-week")
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["slug"] == "documentary-media-week"
        assert payload["details"]["kind"] == "exhibition"
        assert payload["details"]["venue"] == "Main Gallery"
        assert len(payload["details"]["gallery"]) == 2
    finally:
        app.dependency_overrides.pop(events_routes.get_db, None)


def test_event_detail_handles_missing_detail_record(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        seminar = Event(
            slug="seminar-without-detail",
            type="seminar",
            title="Seminar Without Detail",
            is_published=True,
        )
        session.add(seminar)

    app.dependency_overrides[events_routes.get_db] = _override_db(SessionLocal)
    try:
        client = TestClient(app)
        response = client.get("/v1/events/seminar-without-detail")
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["slug"] == "seminar-without-detail"
        # details are optional when supplementary row is missing
        assert payload["details"] is None
    finally:
        app.dependency_overrides.pop(events_routes.get_db, None)
