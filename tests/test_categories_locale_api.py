from __future__ import annotations

import sqlalchemy as sa
from fastapi.testclient import TestClient

from app.api.routes import categories as categories_routes
from app.main import app
from app.models.category import Category, CategoryKind


def seed_category(session, slug: str, name: str, desc: str | None = None, parent: Category | None = None):
    cat = Category(slug=slug, name=name, description=desc, kind=CategoryKind.section, parent=parent)
    session.add(cat)
    session.flush()
    return cat


def upsert_translation(session, category_id: int, locale: str, title: str, description: str | None = None):
    session.execute(
        sa.text(
            """
            INSERT INTO category_translations (category_id, locale, title, description)
            VALUES (:cid, :locale, :title, :description)
            ON CONFLICT(category_id, locale) DO UPDATE
            SET title = excluded.title, description = excluded.description
            """
        ),
        {"cid": category_id, "locale": locale, "title": title, "description": description},
    )


def override_db(SessionLocal):
    def _get_db():
        with SessionLocal() as session:
            try:
                yield session
            finally:
                session.close()
    return _get_db


def test_list_categories_returns_translated_name(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        cat = seed_category(session, "archives", "Archives EN", "Base EN")
        upsert_translation(session, cat.id, "fr", "Archives FR", "Description FR")

    app.dependency_overrides[categories_routes.get_db] = override_db(SessionLocal)
    try:
        with TestClient(app) as client:
            resp = client.get("/v1/categories", params={"locale": "fr", "page_size": 10})
            assert resp.status_code == 200, resp.text
            data = resp.json()
            item = data["items"][0]
            assert item["slug"] == "archives"
            assert item["name"] == "Archives FR"
            assert item["description"] == "Description FR"
    finally:
        app.dependency_overrides.pop(categories_routes.get_db, None)


def test_get_category_returns_translated_name(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        cat = seed_category(session, "archives", "Archives EN", "Base EN")
        upsert_translation(session, cat.id, "es", "Archivos ES", "Descripción ES")

    app.dependency_overrides[categories_routes.get_db] = override_db(SessionLocal)
    try:
        with TestClient(app) as client:
            resp = client.get("/v1/categories/archives", params={"locale": "es"})
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["category"]["slug"] == "archives"
            assert data["category"]["name"] == "Archivos ES"
            assert data["category"]["description"] == "Descripción ES"
    finally:
        app.dependency_overrides.pop(categories_routes.get_db, None)


def test_list_children_returns_translated_name(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        parent = seed_category(session, "root-cat", "Root", "Root EN")
        child = seed_category(session, "child-cat", "Child EN", "Child EN", parent=parent)
        upsert_translation(session, child.id, "ar", "الطفل", "وصف الطفل")

    app.dependency_overrides[categories_routes.get_db] = override_db(SessionLocal)
    try:
        with TestClient(app) as client:
            resp = client.get(f"/v1/categories/{parent.slug}/children", params={"locale": "ar"})
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert len(data["items"]) == 1
            item = data["items"][0]
            assert item["slug"] == "child-cat"
            assert item["name"] == "الطفل"
    finally:
        app.dependency_overrides.pop(categories_routes.get_db, None)
