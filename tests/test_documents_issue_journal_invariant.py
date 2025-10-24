from __future__ import annotations

import pytest

from app.models.document import Document, DocumentType
from app.models.journal import Journal, JournalIssue


def test_document_issue_sets_journal_automatically(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        journal = Journal(slug="stellar-journal", name="Stellar Journal")
        other_journal = Journal(slug="terra-journal", name="Terra Journal")
        issue = JournalIssue(journal=journal, year=2023, volume=1, number=1)

        session.add_all([journal, other_journal, issue])
        session.flush()

        journal_id = journal.id
        other_journal_id = other_journal.id
        issue_id = issue.id

    with SessionLocal.begin() as session:
        doc = Document(
            title="Galactic Discoveries",
            abstract=None,
            type=DocumentType.article,
            lang="en",
            year=2023,
            issue_id=issue_id,
        )
        session.add(doc)
        session.flush()
        assert doc.journal_id == journal_id

    with pytest.raises(ValueError):
        with SessionLocal.begin() as session:
            conflicting_doc = Document(
                title="Contradictory Entry",
                abstract=None,
                type=DocumentType.article,
                lang="en",
                year=2023,
                issue_id=issue_id,
                journal_id=other_journal_id,
            )
            session.add(conflicting_doc)
            session.flush()
