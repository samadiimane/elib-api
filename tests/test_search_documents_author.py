from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.routes import search as search_routes
from app.main import app
from app.models.author import Author, DocumentAuthor
from app.models.category import Category, CategoryKind
from app.models.document import Document, DocumentType


def _create_document_with_author(session, *, title, category, author_name, affiliation, position=1):
    author = Author(
        full_name_ar=author_name,
        full_name_lat=author_name,
        affiliation=affiliation,
    )
    document = Document(
        title=title,
        abstract=None,
        type=DocumentType.article,
        lang="en",
        year=2020,
        primary_category=category,
    )
    session.add_all([author, document])
    session.flush()
    document.author_links.append(DocumentAuthor(author=author, position=position))
    return document


def _override_db(SessionLocal):
    def dependency():
        with SessionLocal() as session:
            try:
                yield session
            finally:
                session.close()

    return dependency


def test_search_documents_by_author_name(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        category = Category(
            slug="library",
            name="Library",
            kind=CategoryKind.section,
        )
        session.add(category)
        session.flush()

        _create_document_with_author(
            session,
            title="Tangier Archives Overview",
            category=category,
            author_name="Fatima Zahra El Idrissi",
            affiliation="University of Rabat",
        )
        _create_document_with_author(
            session,
            title="Casablanca Harbour Notes",
            category=category,
            author_name="Mohamed Ben Youssef",
            affiliation="Casablanca Maritime Institute",
        )

    app.dependency_overrides[search_routes.get_db] = _override_db(SessionLocal)
    try:
        with TestClient(app) as client:
            response = client.get(
                "/v1/search/documents",
                params={"author": "fatima", "page_size": 10},
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["total"] == 1
            assert payload["items"][0]["title"] == "Tangier Archives Overview"
    finally:
        app.dependency_overrides.pop(search_routes.get_db, None)


def test_search_documents_author_with_category(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        root = Category(
            slug="root-category",
            name="Root Category",
            kind=CategoryKind.section,
        )
        matched_category = Category(
            slug="matched",
            name="Matched",
            kind=CategoryKind.topic,
            parent=root,
        )
        other_category = Category(
            slug="other",
            name="Other",
            kind=CategoryKind.topic,
            parent=root,
        )
        session.add_all([root, matched_category, other_category])
        session.flush()

        _create_document_with_author(
            session,
            title="Atlas Forestry Records",
            category=matched_category,
            author_name="Layla Haddad",
            affiliation="Atlas Research Group",
        )
        _create_document_with_author(
            session,
            title="Souss Valley Survey",
            category=other_category,
            author_name="Layla Haddad",
            affiliation="Souss Research Circle",
        )

    app.dependency_overrides[search_routes.get_db] = _override_db(SessionLocal)
    try:
        with TestClient(app) as client:
            response = client.get(
                "/v1/search/documents",
                params={
                    "author": "Layla",
                    "category": "matched",
                    "page_size": 10,
                },
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["total"] == 1
            titles = [item["title"] for item in payload["items"]]
            assert titles == ["Atlas Forestry Records"]
    finally:
        app.dependency_overrides.pop(search_routes.get_db, None)
