from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.routes import categories as categories_routes
from app.main import app
from app.models.category import Category, CategoryKind
from app.models.journal import Journal


def test_categories_api_includes_linked_journal_block(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        journal = Journal(slug="heritage-journal", name="Heritage Journal")
        category = Category(
            slug="heritage-journal",
            name="Heritage Journal",
            kind=CategoryKind.journal,
            journal=journal,
        )
        session.add_all([journal, category])
        session.flush()
        category_slug = category.slug
        journal_id = journal.id

    def override_get_db():
        with SessionLocal() as session:
            try:
                yield session
            finally:
                session.close()

    app.dependency_overrides[categories_routes.get_db] = override_get_db
    try:
        with TestClient(app) as client:
            response = client.get("/v1/categories", params={"page_size": 10})
            assert response.status_code == 200, response.text
            payload = response.json()
            expected_link = {"id": journal_id, "slug": "heritage-journal", "name": "Heritage Journal"}

            assert any(
            item["slug"] == category_slug
            and item.get("linked_journal") == expected_link
            for item in payload["items"]
        )

            detail = client.get(f"/v1/categories/{category_slug}")
            assert detail.status_code == 200, detail.text
            detail_payload = detail.json()
            assert detail_payload["category"]["linked_journal"] == expected_link
    finally:
        app.dependency_overrides.pop(categories_routes.get_db, None)
