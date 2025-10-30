from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.routes import search as search_routes
from app.main import app
from app.models.category import Category, CategoryKind
from app.models.document import Document, DocumentType


def test_search_documents_include_descendants_expands_results(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        root = Category(
            slug="collections",
            name="Collections",
            kind=CategoryKind.section,
        )
        child = Category(
            slug="collections-art",
            name="Collections Art",
            kind=CategoryKind.topic,
            parent=root,
        )
        grandchild = Category(
            slug="collections-art-modern",
            name="Collections Art Modern",
            kind=CategoryKind.topic,
            parent=child,
        )

        doc_child = Document(
            title="Art Catalogue",
            abstract=None,
            type=DocumentType.article,
            lang="fr",
            year=2012,
            primary_category=child,
        )
        doc_grandchild = Document(
            title="Modern Art Notes",
            abstract=None,
            type=DocumentType.report,
            lang="fr",
            year=2015,
            primary_category=grandchild,
        )

        session.add_all([
            root,
            child,
            grandchild,
            doc_child,
            doc_grandchild,
        ])
        session.flush()
        root_slug = root.slug

    def override_get_db():
        with SessionLocal() as session:
            try:
                yield session
            finally:
                session.close()

    app.dependency_overrides[search_routes.get_db] = override_get_db
    try:
        with TestClient(app) as client:
            no_descendants = client.get(
                "/v1/search/documents",
                params={"category": root_slug, "page_size": 10},
            )
            assert no_descendants.status_code == 200, no_descendants.text
            base_payload = no_descendants.json()
            assert base_payload["total"] == 0
            assert base_payload["items"] == []

            with_descendants = client.get(
                "/v1/search/documents",
                params={
                    "category": root_slug,
                    "include_descendants": True,
                    "page_size": 10,
                },
            )
            assert with_descendants.status_code == 200, with_descendants.text
            desc_payload = with_descendants.json()
            assert desc_payload["total"] == 2
            returned_titles = {item["title"] for item in desc_payload["items"]}
            assert returned_titles == {"Art Catalogue", "Modern Art Notes"}
    finally:
        app.dependency_overrides.pop(search_routes.get_db, None)
