from __future__ import annotations

from sqlalchemy import event, select

from app.models.document import Document, DocumentType
from app.models.journal import Journal, JournalIssue
from app.repositories.admin_journals import JournalAdminRepository


def _seed_journals(session) -> tuple[int, int]:
    """Create journals with issues and documents; return their ids."""
    atlas = Journal(name="Atlas Studies", slug="atlas-studies")
    desert = Journal(name="Desert Review", slug="desert-review")
    session.add_all([atlas, desert])
    session.flush()

    session.add_all(
        [
            JournalIssue(journal_id=atlas.id, title="Issue 1"),
            JournalIssue(journal_id=atlas.id, title="Issue 2"),
        ]
    )
    session.add_all(
        [
            Document(
                title="Mapping",
                abstract=None,
                type=DocumentType.article,
                lang="en",
                journal_id=atlas.id,
            ),
            Document(
                title="Atlas Book",
                abstract=None,
                type=DocumentType.book,
                lang="en",
                journal_id=atlas.id,
            ),
        ]
    )
    return atlas.id, desert.id


def test_list_journals_counts_and_query_shape(head_database) -> None:
    SessionLocal, engine = head_database
    with SessionLocal.begin() as session:
        _seed_journals(session)

    counter = {"count": 0}

    def _count_queries(_conn, _cursor, _statement, _params, _ctx, _many):
        counter["count"] += 1

    event.listen(engine, "before_cursor_execute", _count_queries)
    try:
        with SessionLocal() as session:
            repo = JournalAdminRepository(session)
            payload = repo.list_journals(
                q=None,
                status="active",
                page=1,
                page_size=10,
                sort="name",
            )
            assert payload.total == 2
            assert len(payload.items) == 2

            atlas = next(item for item in payload.items if item.slug == "atlas-studies")
            desert = next(item for item in payload.items if item.slug == "desert-review")

            assert atlas.issues_count == 2
            assert atlas.articles_count == 1  # only article type counts
            assert desert.issues_count == 0
            assert desert.articles_count == 0
    finally:
        event.remove(engine, "before_cursor_execute", _count_queries)

    # Two round-trips: one for paged rows, one for total count
    assert counter["count"] <= 2


def test_counts_update_after_deletes(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        atlas_id, _desert_id = _seed_journals(session)

    with SessionLocal.begin() as session:
        # remove one issue and the article
        issue = session.execute(
            select(JournalIssue).where(JournalIssue.journal_id == atlas_id).limit(1)
        ).scalar_one()
        session.delete(issue)

        article = (
            session.execute(
                select(Document).where(
                    Document.journal_id == atlas_id, Document.type == DocumentType.article
                ).limit(1)
            )
            .scalars()
            .first()
        )
        if article:
            session.delete(article)

    with SessionLocal() as session:
        repo = JournalAdminRepository(session)
        payload = repo.list_journals(q=None, status="active", page=1, page_size=10, sort="name")
        atlas = next(item for item in payload.items if item.slug == "atlas-studies")
        assert atlas.issues_count == 1
        assert atlas.articles_count == 0
