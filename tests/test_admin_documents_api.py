from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import auth as auth_dependencies
from app.api.routes import admin_documents as admin_documents_routes
from app.main import app
from app.models.author import Author, DocumentAuthor
from app.models.category import Category, CategoryKind
from app.models.document import Document, DocumentType
from app.models.journal import Journal, JournalIssue
from app.models.user import UserRoleEnum


def _override_db(SessionLocal):
    def dependency():
        with SessionLocal() as session:
            yield session

    return dependency


def _identity(role: UserRoleEnum):
    return SimpleNamespace(
        id=99,
        email="admin-docs@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=role)],
    )


def _apply_overrides(SessionLocal, role: UserRoleEnum = UserRoleEnum.admin):
    app.dependency_overrides[admin_documents_routes.get_db] = _override_db(SessionLocal)
    app.dependency_overrides[auth_dependencies.get_current_user] = lambda: _identity(role)


def _clear_overrides():
    app.dependency_overrides.pop(admin_documents_routes.get_db, None)
    app.dependency_overrides.pop(auth_dependencies.get_current_user, None)


def _seed_document(session):
    category = Category(
        name="Admin Category",
        slug="admin-category",
        kind=CategoryKind.topic,
    )
    journal = Journal(
        name="Admin Journal",
        slug="admin-journal",
    )
    issue = JournalIssue(
        journal=journal,
        year=2024,
        volume=1,
        number=2,
        title="Special Issue",
    )
    author_one = Author(full_name_ar="Author One AR", full_name_lat="Author One")
    author_two = Author(full_name_ar="Author Two AR", full_name_lat="Author Two")
    document = Document(
        title="Admin Document",
        abstract="Admin abstract body",
        type=DocumentType.article,
        lang="en",
        year=2024,
        pages=12,
        primary_category=category,
        journal=journal,
        issue=issue,
        start_page=5,
        end_page=16,
        doi="10.1234/admin-doc",
        isbn="ISBN-1234",
        issn="ISSN-5678",
        cover_image_url="https://cdn.example.org/cover.jpg",
    )
    document.author_links = [
        DocumentAuthor(author=author_one, position=1),
        DocumentAuthor(author=author_two, position=2),
    ]
    session.add(document)
    session.flush()
    return document, journal, issue, category, [author_one, author_two]


def _seed_category(session, *, slug: str, kind: CategoryKind, name: str = "Cat"):
    category = Category(slug=slug, name=name, kind=kind)
    session.add(category)
    session.flush()
    return category


def test_admin_documents_requires_admin_role(head_database) -> None:
    SessionLocal, _engine = head_database
    _apply_overrides(SessionLocal, role=UserRoleEnum.researcher)
    try:
        client = TestClient(app)
        response = client.get("/v1/admin/documents")
        assert response.status_code == 403
    finally:
        _clear_overrides()


def test_admin_documents_list_and_filters(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        document, journal, issue, category, authors = _seed_document(session)
        doc_id = document.id
        journal_id = journal.id
        issue_id = issue.id
        category_id = category.id
        first_author_lat = authors[0].full_name_lat

    _apply_overrides(SessionLocal)
    try:
        client = TestClient(app)
        response = client.get(
            "/v1/admin/documents",
            params={"q": "Admin", "page_size": 10, "journal_id": journal_id},
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["total"] == 1
        assert payload["has_next"] is False
        assert len(payload["items"]) == 1
        item = payload["items"][0]
        assert item["id"] == doc_id
        assert item["journal"]["id"] == journal_id
        assert item["issue"]["id"] == issue_id
        assert item["primary_category"]["id"] == category_id
        assert item["authors"][0]["name_lat"] == first_author_lat
        assert item["status"] == "active"
    finally:
        _clear_overrides()


def test_admin_documents_detail_returns_full_payload(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        document, journal, issue, category, _authors = _seed_document(session)
        document_id = document.id
        issue_year = issue.year
        category_slug = category.slug

    _apply_overrides(SessionLocal)
    try:
        client = TestClient(app)
        response = client.get(f"/v1/admin/documents/{document_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == document_id
        assert data["doi"] == "10.1234/admin-doc"
        assert data["start_page"] == 5
        assert data["end_page"] == 16
        assert data["issue"]["year"] == issue_year
        assert data["primary_category"]["slug"] == category_slug
    finally:
        _clear_overrides()


def test_create_document_enforces_issue_journal_and_type(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        _doc, journal, issue, category, authors = _seed_document(session)
        issue_id = issue.id
        journal_id = journal.id
        wrong_journal = Journal(name="Wrong", slug="wrong")
        session.add(wrong_journal)
        session.flush()
        wrong_journal_id = wrong_journal.id
        category_id = category.id
        author_ids = [author.id for author in authors]

    _apply_overrides(SessionLocal)
    try:
        client = TestClient(app)
        payload = {
          "title": "New Article",
          "lang": "en",
          "issue_id": issue_id,
          "journal_id": wrong_journal_id,
          "primary_category_id": category_id,
          "author_ids": [author_ids[0]],
        }
        response = client.post("/v1/admin/documents", json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["issue"]["id"] == issue_id
        assert data["journal"]["id"] == journal_id
        assert data["type"] == "article"
    finally:
        _clear_overrides()


def test_create_document_for_archive_forces_archive_item(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        archive_category = _seed_category(session, slug="archive-cat", kind=CategoryKind.archive_collection)
        archive_category_id = archive_category.id

    _apply_overrides(SessionLocal)
    try:
        client = TestClient(app)
        payload = {"title": "Archive Doc", "lang": "fr", "primary_category_id": archive_category_id}
        response = client.post("/v1/admin/documents", json=payload)
        assert response.status_code == 201, response.text
        assert response.json()["type"] == "archive_item"
    finally:
        _clear_overrides()


def test_invalid_year_returns_422(head_database) -> None:
    SessionLocal, _engine = head_database
    _apply_overrides(SessionLocal)
    try:
        client = TestClient(app)
        payload = {"title": "Bad Year", "lang": "en", "year": 1700}
        response = client.post("/v1/admin/documents", json=payload)
        assert response.status_code == 422
        assert "Year" in response.json()["detail"]["user_message"]
    finally:
        _clear_overrides()


def test_soft_deleted_author_rejected(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        author = Author(full_name_ar="Old", full_name_lat="Old", deleted_at=datetime.now(timezone.utc))
        session.add(author)
        session.flush()
        author_id = author.id

    _apply_overrides(SessionLocal)
    try:
        client = TestClient(app)
        payload = {"title": "Doc", "lang": "en", "author_ids": [author_id]}
        response = client.post("/v1/admin/documents", json=payload)
        assert response.status_code == 422
    finally:
        _clear_overrides()


def test_admin_documents_soft_delete_and_restore(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        document, _journal, _issue, _category, _authors = _seed_document(session)
        document_id = document.id

    _apply_overrides(SessionLocal)
    try:
        client = TestClient(app)
        delete_resp = client.patch(f"/v1/admin/documents/{document_id}/delete")
        assert delete_resp.status_code == 200, delete_resp.text
        assert delete_resp.json()["status"] == "deleted"

        active_list = client.get("/v1/admin/documents", params={"status": "active"})
        assert active_list.status_code == 200
        assert active_list.json()["total"] == 0

        deleted_list = client.get("/v1/admin/documents", params={"status": "deleted"})
        assert deleted_list.status_code == 200
        assert deleted_list.json()["total"] == 1
        assert deleted_list.json()["items"][0]["status"] == "deleted"

        restore_resp = client.patch(f"/v1/admin/documents/{document_id}/restore")
        assert restore_resp.status_code == 200
        assert restore_resp.json()["status"] == "active"

        active_after = client.get("/v1/admin/documents", params={"status": "active"})
        assert active_after.status_code == 200
        assert active_after.json()["total"] == 1

        deleted_after = client.get("/v1/admin/documents", params={"status": "deleted"})
        assert deleted_after.status_code == 200
        assert deleted_after.json()["total"] == 0
    finally:
        _clear_overrides()
