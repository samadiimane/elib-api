from __future__ import annotations

from app.models.category import Category, CategoryKind
from app.models.document import Document, DocumentType
from app.models.journal import Journal
from app.repositories.documents import build_base_filters, facet_counts_by_category


def test_search_category_with_journal_maps_to_journal_filter(head_database) -> None:
    SessionLocal, _engine = head_database

    with SessionLocal.begin() as session:
        journal = Journal(slug="atlas-journal", name="Atlas Journal")
        journal_cat = Category(
            slug="atlas-journal",
            name="Atlas Journal",
            kind=CategoryKind.journal,
            journal=journal,
        )
        topic_cat = Category(
            slug="world-history",
            name="World History",
            kind=CategoryKind.topic,
        )

        doc_with_primary = Document(
            title="Mapping the World",
            abstract=None,
            type=DocumentType.article,
            lang="en",
            year=2020,
            journal=journal,
            primary_category=topic_cat,
        )
        doc_without_primary = Document(
            title="Atlas Addendum",
            abstract=None,
            type=DocumentType.article,
            lang="en",
            year=2021,
            journal=journal,
        )
        doc_other = Document(
            title="Unrelated Topic",
            abstract=None,
            type=DocumentType.article,
            lang="en",
            year=2022,
            primary_category=topic_cat,
        )

        session.add_all([
            journal,
            journal_cat,
            topic_cat,
            doc_with_primary,
            doc_without_primary,
            doc_other,
        ])
        session.flush()

        journal_category_slug = journal_cat.slug
        topic_category_slug = topic_cat.slug
        expected_journal_doc_ids = {doc_with_primary.id, doc_without_primary.id}
        expected_topic_doc_ids = {doc_with_primary.id, doc_other.id}

    with SessionLocal() as session:
        journal_base = build_base_filters(session, category_slug=journal_category_slug)
        journal_docs = session.execute(journal_base).scalars().all()
        assert {doc.id for doc in journal_docs} == expected_journal_doc_ids

        topic_base = build_base_filters(session, category_slug=topic_category_slug)
        topic_docs = session.execute(topic_base).scalars().all()
        assert {doc.id for doc in topic_docs} == expected_topic_doc_ids

        journal_with_desc = build_base_filters(
            session,
            category_slug=journal_category_slug,
            include_descendants=True,
        )
        journal_desc_docs = session.execute(journal_with_desc).scalars().all()
        assert {doc.id for doc in journal_desc_docs} == expected_journal_doc_ids

        topic_with_desc = build_base_filters(
            session,
            category_slug=topic_category_slug,
            include_descendants=True,
        )
        topic_desc_docs = session.execute(topic_with_desc).scalars().all()
        assert {doc.id for doc in topic_desc_docs} == expected_topic_doc_ids

        journal_facets = facet_counts_by_category(session, journal_base)
        assert all(slug != journal_category_slug for slug, _name, _count in journal_facets)
