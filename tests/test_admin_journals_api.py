from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import auth as auth_dependencies
from app.api.routes import admin_journals as admin_journals_routes
from app.main import app
from app.models.document import Document, DocumentType
from app.models.journal import Journal, JournalIssue
from app.models.user import UserRoleEnum


def _override_db(SessionLocal):
    def dependency():
        with SessionLocal() as session:
            yield session

    return dependency


def _admin_identity():
    return SimpleNamespace(
        id=7,
        email="admin@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=UserRoleEnum.admin)],
    )


def _non_admin_identity():
    return SimpleNamespace(
        id=8,
        email="viewer@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=UserRoleEnum.researcher)],
    )


def _apply_overrides(SessionLocal, identity):
    app.dependency_overrides[admin_journals_routes.get_db] = _override_db(SessionLocal)
    app.dependency_overrides[auth_dependencies.get_current_user] = lambda: identity


def _clear_overrides():
    app.dependency_overrides.pop(admin_journals_routes.get_db, None)
    app.dependency_overrides.pop(auth_dependencies.get_current_user, None)


def test_list_journals_requires_admin(head_database):
    SessionLocal, _engine = head_database
    _apply_overrides(SessionLocal, _non_admin_identity())
    client = TestClient(app)
    try:
        response = client.get("/v1/admin/journals")
        assert response.status_code == 403
    finally:
        _clear_overrides()


def test_list_journals_includes_counts_and_filters(head_database):
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        active = Journal(name="Atlas Studies", slug="atlas-studies")
        deleted = Journal(name="Desert Review", slug="desert-review", deleted_at=datetime.now(timezone.utc))
        session.add_all([active, deleted])
        session.flush()

        issue = JournalIssue(journal_id=active.id, title="Issue 1")
        doc_article = Document(
            title="Mapping the Desert",
            abstract=None,
            type=DocumentType.article,
            lang="en",
            journal_id=active.id,
        )
        doc_other = Document(
            title="Atlas Compendium",
            abstract=None,
            type=DocumentType.book,
            lang="en",
            journal_id=active.id,
        )
        session.add_all([issue, doc_article, doc_other])

    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        response = client.get("/v1/admin/journals", params={"status": "active", "page_size": 10})
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        item = payload["items"][0]
        assert item["issues_count"] == 1
        assert item["articles_count"] == 1
        assert item["slug"] == "atlas-studies"

        include_deleted = client.get("/v1/admin/journals", params={"status": "all", "q": "desert"})
        assert include_deleted.status_code == 200
        assert include_deleted.json()["items"][0]["slug"] == "desert-review"
    finally:
        _clear_overrides()


def test_create_journal_and_enforce_unique_slug(head_database):
    SessionLocal, _engine = head_database
    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        response = client.post(
            "/v1/admin/journals",
            json={"name": "Heritage Review", "description": "Culture insights"},
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["slug"] == "heritage-review"
        assert payload["issues_count"] == 0
        assert payload["articles_count"] == 0

        dup = client.post(
            "/v1/admin/journals",
            json={"name": "Another", "slug": "Heritage Review"},
        )
        assert dup.status_code == 409
        detail = dup.json()["detail"]
        assert detail["code"] == "JOURNAL_SLUG_EXISTS"

        with SessionLocal() as session:
            stored = session.execute(select(Journal).where(Journal.slug == "heritage-review")).scalar_one()
            assert stored.description == "Culture insights"
    finally:
        _clear_overrides()


def test_update_journal_and_slug_conflict(head_database):
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        first = Journal(name="Journal One", slug="journal-one")
        second = Journal(name="Journal Two", slug="journal-two")
        session.add_all([first, second])
        session.flush()
        first_id = first.id
        second_id = second.id

    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        update_response = client.patch(
            f"/v1/admin/journals/{first_id}",
            json={"name": "Updated Journal", "slug": "updated-journal", "cover_image_url": "https://cdn/img.jpg"},
        )
        assert update_response.status_code == 200, update_response.text
        updated = update_response.json()
        assert updated["slug"] == "updated-journal"
        assert updated["name"] == "Updated Journal"
        assert updated["cover_image_url"] == "https://cdn/img.jpg"

        conflict = client.patch(
            f"/v1/admin/journals/{first_id}",
            json={"slug": "journal-two"},
        )
        assert conflict.status_code == 409
        detail = conflict.json()["detail"]
        assert detail["code"] == "JOURNAL_SLUG_EXISTS"

        with SessionLocal() as session:
            stored = session.execute(select(Journal).where(Journal.id == first_id)).scalar_one()
            assert stored.slug == "updated-journal"
            assert session.execute(select(Journal).where(Journal.id == second_id)).scalar_one().slug == "journal-two"
    finally:
        _clear_overrides()


def test_soft_delete_and_restore_journal(head_database):
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        journal = Journal(name="Chronicles", slug="chronicles")
        session.add(journal)
        session.flush()
        journal_id = journal.id

    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        delete_response = client.patch(f"/v1/admin/journals/{journal_id}/soft-delete")
        assert delete_response.status_code == 204

        active = client.get("/v1/admin/journals")
        assert active.status_code == 200
        assert active.json()["total"] == 0

        deleted = client.get("/v1/admin/journals", params={"status": "deleted"})
        assert deleted.status_code == 200
        assert deleted.json()["total"] == 1
        assert deleted.json()["items"][0]["deleted_at"] is not None

        restore_response = client.patch(f"/v1/admin/journals/{journal_id}/restore")
        assert restore_response.status_code == 204

        after_restore = client.get("/v1/admin/journals")
        assert after_restore.status_code == 200
        assert after_restore.json()["total"] == 1
        assert after_restore.json()["items"][0]["deleted_at"] is None
    finally:
        _clear_overrides()
