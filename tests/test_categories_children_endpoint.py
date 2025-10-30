from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.routes import categories as categories_routes
from app.main import app
from app.models.category import Category, CategoryKind
from app.models.document import Document, DocumentType


def test_category_children_endpoint_returns_children_with_counts(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        parent = Category(
            slug="history",
            name="History",
            kind=CategoryKind.topic,
        )
        topic_child = Category(
            slug="ancient-history",
            name="Ancient History",
            kind=CategoryKind.topic,
            parent=parent,
        )
        section_child = Category(
            slug="history-section",
            name="History Section",
            kind=CategoryKind.section,
            parent=parent,
        )
        other_topic = Category(
            slug="modern-history",
            name="Modern History",
            kind=CategoryKind.topic,
            parent=parent,
        )
        grandchild = Category(
            slug="ancient-rome",
            name="Ancient Rome",
            kind=CategoryKind.topic,
            parent=topic_child,
        )

        doc_primary = Document(
            title="Empire Records",
            abstract=None,
            type=DocumentType.article,
            lang="en",
            year=1999,
            primary_category=topic_child,
        )
        doc_descendant = Document(
            title="Rise of Rome",
            abstract=None,
            type=DocumentType.book,
            lang="en",
            year=2001,
            primary_category=grandchild,
        )
        doc_other_topic = Document(
            title="Modern Revolutions",
            abstract=None,
            type=DocumentType.article,
            lang="en",
            year=2010,
            primary_category=other_topic,
        )

        session.add_all([
            parent,
            topic_child,
            section_child,
            other_topic,
            grandchild,
            doc_primary,
            doc_descendant,
            doc_other_topic,
        ])
        session.flush()
        parent_slug = parent.slug

    def override_get_db():
        with SessionLocal() as session:
            try:
                yield session
            finally:
                session.close()

    app.dependency_overrides[categories_routes.get_db] = override_get_db
    try:
        with TestClient(app) as client:
            response = client.get(
                f"/v1/categories/{parent_slug}/children",
                params={"with_counts": True},
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert [item["slug"] for item in payload["items"]] == [
                "ancient-history",
                "history-section",
                "modern-history",
            ]
            counts = {
                item["slug"]: item.get("counts", {}).get("documents")
                for item in payload["items"]
            }
            assert counts["ancient-history"] == 2
            assert counts["modern-history"] == 1
            assert counts["history-section"] == 0

            filtered = client.get(
                f"/v1/categories/{parent_slug}/children",
                params={"kind": CategoryKind.topic.value},
            )
            assert filtered.status_code == 200, filtered.text
            filtered_items = filtered.json()["items"]
            assert [item["slug"] for item in filtered_items] == [
                "ancient-history",
                "modern-history",
            ]
            assert all(item.get("counts") is None for item in filtered_items)
    finally:
        app.dependency_overrides.pop(categories_routes.get_db, None)
