from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import auth as auth_dependencies
from app.api.routes import admin_authors as admin_authors_routes
from app.main import app
from app.models.author import Author
from app.models.user import UserRoleEnum


def _override_db(SessionLocal):
    def dependency():
        with SessionLocal() as session:
            yield session

    return dependency


def _admin_identity():
    return SimpleNamespace(
        id=99,
        email="admin@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=UserRoleEnum.admin)],
    )


def _non_admin_identity():
    return SimpleNamespace(
        id=100,
        email="viewer@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=UserRoleEnum.researcher)],
    )


def _apply_overrides(SessionLocal, identity):
    app.dependency_overrides[admin_authors_routes.get_db] = _override_db(SessionLocal)
    app.dependency_overrides[auth_dependencies.get_current_user] = lambda: identity


def _clear_overrides():
    app.dependency_overrides.pop(admin_authors_routes.get_db, None)
    app.dependency_overrides.pop(auth_dependencies.get_current_user, None)


def test_list_authors_requires_admin(head_database):
    SessionLocal, _engine = head_database
    _apply_overrides(SessionLocal, _non_admin_identity())
    client = TestClient(app)
    try:
        response = client.get("/v1/admin/authors")
        assert response.status_code == 403
    finally:
        _clear_overrides()


def test_list_authors_returns_paginated_results(head_database):
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        session.add_all(
            [
                Author(full_name_ar="الخوارزمي", full_name_lat="Al Khwarizmi", affiliation="House of Wisdom", slug="al-khwarizmi"),
                Author(full_name_ar="ابن رشد", full_name_lat="Ibn Rushd", affiliation="Cordoba", slug="ibn-rushd"),
                Author(full_name_ar="ابن سينا", full_name_lat="Ibn Sina", affiliation="Bukhara", slug="ibn-sina"),
            ]
        )

    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        response = client.get("/v1/admin/authors", params={"page": 1, "page_size": 2, "sort": "name"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["page"] == 1
        assert payload["page_size"] == 2
        assert payload["total"] == 3
        assert len(payload["items"]) == 2
        latin_names = [item["name_latin"] for item in payload["items"]]
        assert latin_names == sorted(latin_names)

        search = client.get("/v1/admin/authors", params={"q": "khw", "page": 1, "page_size": 10})
        assert search.status_code == 200
        assert search.json()["items"][0]["slug"] == "al-khwarizmi"
    finally:
        _clear_overrides()


def test_create_author_success_and_duplicate_slug(head_database):
    SessionLocal, _engine = head_database
    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        payload = {
            "name_latin": "Fatima al-Fihri",
            "name_ar": "فاطمة الفهرية",
            "affiliation": "University of al-Qarawiyyin",
        }
        response = client.post("/v1/admin/authors", json=payload)
        assert response.status_code == 201, response.text
        created = response.json()
        assert created["name_latin"] == payload["name_latin"]
        assert created["name_ar"] == payload["name_ar"]
        assert created["affiliation"] == payload["affiliation"]
        assert created["slug"] == "fatima-al-fihri"

        duplicate = client.post("/v1/admin/authors", json={"name_latin": "Fatima al-Fihri"})
        assert duplicate.status_code == 409
        assert "user_message" in duplicate.json()["detail"]

        with SessionLocal() as session:
            stored = session.execute(select(Author).where(Author.slug == "fatima-al-fihri")).scalar_one()
            assert stored.full_name_ar == payload["name_ar"]
    finally:
        _clear_overrides()
