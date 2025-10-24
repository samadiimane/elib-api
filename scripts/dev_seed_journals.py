"""Seed journals, their issues, and representative scholarly articles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Category, CategoryKind, Document, DocumentType, Journal, JournalIssue
from sqlalchemy.orm import configure_mappers

configure_mappers()


@dataclass(frozen=True)
class ArticleSeed:
    title: str
    abstract: str
    lang: str
    year: int
    start_page: int | None = None
    end_page: int | None = None
    topic_slug: str | None = None

    @property
    def page_span(self) -> int | None:
        if self.start_page is None or self.end_page is None:
            return None
        return max(self.end_page - self.start_page + 1, 1)


@dataclass(frozen=True)
class IssueSeed:
    year: int
    volume: int | None
    number: int | None
    title: str | None = None
    articles: tuple[ArticleSeed, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class JournalSeed:
    slug: str
    name: str
    description: str | None = None
    issn: str | None = None
    publisher: str | None = None
    category_description: str | None = None
    issues: tuple[IssueSeed, ...] = field(default_factory=tuple)


JOURNAL_SEEDS: tuple[JournalSeed, ...] = (
    JournalSeed(
        slug="maghribi-studies-review",
        name="Maghribi Studies Review",
        issn="2790-1123",
        publisher="Centre for Maghribi Historical Studies",
        description="Interdisciplinary journal on the social, cultural, and intellectual histories of the western Mediterranean.",
        category_description="Peer-reviewed articles on Maghribi history, anthropology, and archival sciences.",
        issues=(
            IssueSeed(
                year=2023,
                volume=12,
                number=1,
                title="Urban Archives and Social Memory",
                articles=(
                    ArticleSeed(
                        title="Reassembling the Tangier Municipal Archives",
                        abstract="Examines the custodial history of municipal ledgers to trace urban governance reforms from 1890 to 1930.",
                        lang="en",
                        year=2023,
                        start_page=1,
                        end_page=28,
                        topic_slug="urban-histories",
                    ),
                    ArticleSeed(
                        title="Public Health Ledgers as Social Biography",
                        abstract="Explores how epidemic registers became instruments for negotiating citizenship and residence in port cities.",
                        lang="en",
                        year=2023,
                        start_page=29,
                        end_page=54,
                        topic_slug="material-culture",
                    ),
                ),
            ),
            IssueSeed(
                year=2023,
                volume=12,
                number=2,
                title="Maritime Crossings",
                articles=(
                    ArticleSeed(
                        title="Logbooks of the Maghribi Steamship Consortium",
                        abstract="Analyzes bilingual logbooks to reconstruct commercial diplomacy across Tangier, Marseille, and Liverpool.",
                        lang="en",
                        year=2023,
                        start_page=5,
                        end_page=33,
                        topic_slug="intellectual-networks",
                    ),
                    ArticleSeed(
                        title="Sailors, Saints, and Shoreline Shrines",
                        abstract="Documents votive practices of maritime guilds and their entanglement with coastal Sufi lodges.",
                        lang="fr",
                        year=2023,
                        start_page=34,
                        end_page=61,
                        topic_slug="sacred-architecture",
                    ),
                ),
            ),
        ),
    ),
    JournalSeed(
        slug="revue-histoire-mediterraneenne",
        name="Revue d'Histoire Mediterraneenne",
        issn="1987-4475",
        publisher="Institut des Etudes Mediterraneennes",
        description="French-language quarterly dedicated to comparative Mediterranean histories from the sixteenth century onward.",
        category_description="Comparative Mediterranean scholarship with emphasis on Franco-Maghribi exchanges.",
        issues=(
            IssueSeed(
                year=2022,
                volume=18,
                number=3,
                title="Intellectual Circulations",
                articles=(
                    ArticleSeed(
                        title="Correspondances savantes entre Fes et Marseille",
                        abstract="Publishes and interprets a cache of scholarly correspondence charting botanical exchanges between 1845 and 1860.",
                        lang="fr",
                        year=2022,
                        start_page=11,
                        end_page=42,
                        topic_slug="intellectual-networks",
                    ),
                    ArticleSeed(
                        title="Traduire la Medecine Arabe pour l'Ecole de Montpellier",
                        abstract="Studies translation committees that rendered Maghribi pharmacopoeias into French pedagogical manuals.",
                        lang="fr",
                        year=2022,
                        start_page=43,
                        end_page=71,
                        topic_slug="material-culture",
                    ),
                ),
            ),
        ),
    ),
    JournalSeed(
        slug="majallat-al-athar",
        name="Majallat al-Athar",
        issn="3001-5520",
        publisher="Markaz al-Buhuth al-Turathiyya",
        description="Arabic-language review dedicated to archaeology, architectural conservation, and museology across North Africa.",
        category_description="Arabic scholarship on conservation science, excavation reports, and museological debates.",
        issues=(
            IssueSeed(
                year=2024,
                volume=7,
                number=1,
                title="Techniques of Preservation",
                articles=(
                    ArticleSeed(
                        title="Istiratijiyyat li-Tawthiq al-Qila' al-Sahiliyya",
                        abstract="Assesses digital photogrammetry workflows for safeguarding coastal fortifications in northern Morocco.",
                        lang="ar",
                        year=2024,
                        start_page=3,
                        end_page=27,
                        topic_slug="coastal-forts",
                    ),
                    ArticleSeed(
                        title="Ma'arid al-Mawrid al-Turathi fi al-Matarih al-Jabaliyya",
                        abstract="Evaluates community-curated exhibitions as custodians of mountain shrine material culture.",
                        lang="ar",
                        year=2024,
                        start_page=28,
                        end_page=52,
                        topic_slug="sacred-architecture",
                    ),
                ),
            ),
        ),
    ),
    JournalSeed(
        slug="dar-al-niaba",
        name="Dar al-Niaba",
        issn="1607-4410",
        publisher="Société des Études Tangéroises",
        description="Historical bulletin devoted to the diplomatic, legal, and urban cultures of Tangier under international administration.",
        category_description="Bulletins and scholarly dossiers on Tangier's international zone, consular corps, and municipal reforms.",
        issues=(
            IssueSeed(
                year=1930,
                volume=5,
                number=1,
                title="Tangier and the International Zone",
                articles=(
                    ArticleSeed(
                        title="Minutes of the International Legislative Assembly, Spring 1930",
                        abstract="Critical edition of assembly minutes highlighting negotiations over port tariffs and public health ordinances.",
                        lang="fr",
                        year=1930,
                        start_page=3,
                        end_page=37,
                        topic_slug="urban-histories",
                    ),
                    ArticleSeed(
                        title="Consular Courts and the Regulation of Commercial Disputes",
                        abstract="Analyzes precedents from the British and Spanish consular courts, illustrating hybrid legal reasoning.",
                        lang="en",
                        year=1930,
                        start_page=38,
                        end_page=64,
                        topic_slug="intellectual-networks",
                    ),
                ),
            ),
            IssueSeed(
                year=1931,
                volume=5,
                number=2,
                title="Urban Services and Civic Modernity",
                articles=(
                    ArticleSeed(
                        title="Mapping Municipal Infrastructure in the Kasbah Quarter",
                        abstract="Uses cadastral maps and engineering memoranda to trace electrification and water provision schemes.",
                        lang="fr",
                        year=1931,
                        start_page=5,
                        end_page=29,
                        topic_slug="urban-histories",
                    ),
                    ArticleSeed(
                        title="Public Ceremonies at Dar al-Makhzen",
                        abstract="Ethnographic description of ceremonial spaces and their adaptation to diplomatic choreographies.",
                        lang="ar",
                        year=1931,
                        start_page=30,
                        end_page=56,
                        topic_slug="sacred-architecture",
                    ),
                ),
            ),
        ),
    ),
    JournalSeed(
        slug="les-tangerois",
        name="Les Tangérois",
        issn="1764-8820",
        publisher="Association Mémoire de Tanger",
        description="Francophone review chronicling civic associations, literary salons, and cultural life in Tangier throughout the twentieth century.",
        category_description="Literary and civic histories centred on Tangier's multilingual communities.",
        issues=(
            IssueSeed(
                year=1957,
                volume=2,
                number=3,
                title="Saisons Littéraires",
                articles=(
                    ArticleSeed(
                        title="Chronique des Salons Littéraires Tangérois",
                        abstract="Profiles vernacular literary salons, situating their readings within Mediterranean circuits of translation.",
                        lang="fr",
                        year=1957,
                        start_page=9,
                        end_page=33,
                        topic_slug="intellectual-networks",
                    ),
                    ArticleSeed(
                        title="Photographier Tanger: Archives de la Modernité",
                        abstract="Analyzes amateur photography clubs as custodians of urban memory and modernist aesthetics.",
                        lang="fr",
                        year=1957,
                        start_page=34,
                        end_page=58,
                        topic_slug="material-culture",
                    ),
                ),
            ),
            IssueSeed(
                year=1958,
                volume=3,
                number=1,
                title="Sociétés Civiles en Mutation",
                articles=(
                    ArticleSeed(
                        title="Associations de Quartier et Economies Solidaires",
                        abstract="Documents neighbourhood associations that managed cooperative bakeries and mutual aid funds during decolonization.",
                        lang="fr",
                        year=1958,
                        start_page=5,
                        end_page=28,
                        topic_slug="urban-histories",
                    ),
                    ArticleSeed(
                        title="Musique Andalouse et Identités Citadines",
                        abstract="Explores ensembles that bridged Andalusi repertoires with emerging civic identities in Tangier.",
                        lang="fr",
                        year=1958,
                        start_page=29,
                        end_page=52,
                        topic_slug="material-culture",
                    ),
                ),
            ),
        ),
    ),
)


def get_or_create_category(
    session,
    *,
    slug: str,
    name: str,
    kind: CategoryKind,
    description: str | None,
    parent: Category | None,
) -> Category:
    stmt = select(Category).where(Category.slug == slug)
    category = session.execute(stmt).scalar_one_or_none()
    if category:
        category.name = name
        category.kind = kind
        category.description = description
        if parent and category.parent_id != parent.id:
            category.parent = parent
        return category

    category = Category(
        slug=slug,
        name=name,
        kind=kind,
        description=description,
        parent=parent,
    )
    session.add(category)
    session.flush()
    return category


def get_category_by_slug(session, slug: str) -> Category | None:
    stmt = select(Category).where(Category.slug == slug)
    return session.execute(stmt).scalar_one_or_none()


def upsert_journal(session, seed: JournalSeed, journals_parent: Category) -> Journal:
    stmt = select(Journal).where(Journal.slug == seed.slug)
    journal = session.execute(stmt).scalar_one_or_none()
    if journal:
        journal.name = seed.name
        journal.description = seed.description
        journal.issn = seed.issn
        journal.publisher = seed.publisher
    else:
        journal = Journal(
            slug=seed.slug,
            name=seed.name,
            description=seed.description,
            issn=seed.issn,
            publisher=seed.publisher,
        )
        session.add(journal)
        session.flush()

    category = get_or_create_category(
        session,
        slug=seed.slug,
        name=seed.name,
        kind=CategoryKind.journal,
        description=seed.category_description,
        parent=journals_parent,
    )
    category.journal = journal
    return journal


def upsert_issue(session, journal: Journal, seed: IssueSeed) -> JournalIssue:
    stmt = (
        select(JournalIssue)
        .where(JournalIssue.journal_id == journal.id)
        .where(JournalIssue.year == seed.year)
        .where(JournalIssue.volume == seed.volume)
        .where(JournalIssue.number == seed.number)
    )
    issue = session.execute(stmt).scalar_one_or_none()
    if issue:
        issue.title = seed.title
    else:
        issue = JournalIssue(
            journal=journal,
            year=seed.year,
            volume=seed.volume,
            number=seed.number,
            title=seed.title,
        )
        session.add(issue)
        session.flush()
    return issue


def upsert_article(session, journal: Journal, issue: JournalIssue, seed: ArticleSeed) -> None:
    stmt = select(Document).where(Document.title == seed.title)
    document = session.execute(stmt).scalar_one_or_none()
    topic = get_category_by_slug(session, seed.topic_slug) if seed.topic_slug else None

    if document:
        document.abstract = seed.abstract
        document.lang = seed.lang
        document.year = seed.year
        document.start_page = seed.start_page
        document.end_page = seed.end_page
        document.pages = seed.page_span
        document.issue = issue
        document.journal = journal
        document.primary_category = topic
        return

    document = Document(
        title=seed.title,
        abstract=seed.abstract,
        type=DocumentType.article,
        lang=seed.lang,
        year=seed.year,
        pages=seed.page_span,
        start_page=seed.start_page,
        end_page=seed.end_page,
        journal=journal,
        issue=issue,
        primary_category=topic,
    )
    session.add(document)


def run() -> None:
    session = SessionLocal()
    try:
        journals_parent = get_or_create_category(
            session,
            slug="journals",
            name="Journals",
            kind=CategoryKind.section,
            description="Serial publications that disseminate peer-reviewed scholarship across Maghribi studies.",
            parent=None,
        )

        for journal_seed in JOURNAL_SEEDS:
            journal = upsert_journal(session, journal_seed, journals_parent)
            for issue_seed in journal_seed.issues:
                issue = upsert_issue(session, journal, issue_seed)
                for article_seed in issue_seed.articles:
                    upsert_article(session, journal, issue, article_seed)

        session.commit()
        print("Seeded journals, issues, and representative articles.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
