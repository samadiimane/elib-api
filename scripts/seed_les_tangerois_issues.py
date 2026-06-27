"""Seed Les Tangérois whole-issue PDF documents.

Usage:
    python -m scripts.seed_les_tangerois_issues
    python -m scripts.seed_les_tangerois_issues les-tangerois-08
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts.dar_al_niaba_seed_common import run_issue


JOURNAL_SLUG = "les-tangerois"
JOURNAL_NAME = "Les Tangérois"


def issue_config(*, title: str, year: int, volume: int, number: int) -> dict:
    return {
        "journal_slug": JOURNAL_SLUG,
        "journal_name": JOURNAL_NAME,
        "title": title,
        "year": year,
        "volume": volume,
        "number": number,
    }


def whole_issue_article(*, title: str, doc_id: str) -> dict:
    return {
        "title": f"العدد الكامل: {title}",
        "authors": [],
        "lang": "ar",
        "pages": None,
        "start_page": None,
        "end_page": None,
        "file_key": f"{JOURNAL_SLUG}/{doc_id}.pdf",
    }


ISSUES = [
    (
        issue_config(
            title="العدد الثامن، السنة الثانية، خريف 2003",
            year=2003,
            volume=2,
            number=8,
        ),
        [
            whole_issue_article(
                title="العدد الثامن، السنة الثانية، خريف 2003",
                doc_id="les-tangerois-08",
            )
        ],
    ),
    (
        issue_config(
            title="العدد التاسع، السنة الثالثة، شتاء 2004",
            year=2004,
            volume=3,
            number=9,
        ),
        [
            whole_issue_article(
                title="العدد التاسع، السنة الثالثة، شتاء 2004",
                doc_id="les-tangerois-09",
            )
        ],
    ),
    (
        issue_config(
            title="العدد العاشر، السنة الثالثة، ربيع 2004",
            year=2004,
            volume=3,
            number=10,
        ),
        [
            whole_issue_article(
                title="العدد العاشر، السنة الثالثة، ربيع 2004",
                doc_id="les-tangerois-10",
            )
        ],
    ),
    (
        issue_config(
            title="العدد الثاني عشر، السنة الثالثة، شتاء 2004",
            year=2004,
            volume=3,
            number=12,
        ),
        [
            whole_issue_article(
                title="العدد الثاني عشر، السنة الثالثة، شتاء 2004",
                doc_id="les-tangerois-12",
            )
        ],
    ),
]


def article_doc_id(article: dict) -> str:
    return Path(article["file_key"]).stem


def run(doc_ids=()) -> None:
    requested = set(doc_ids)
    all_doc_ids = {article_doc_id(article) for _, articles in ISSUES for article in articles}
    missing = requested - all_doc_ids
    if missing:
        raise SystemExit(f"Unknown doc_id(s): {', '.join(sorted(missing))}")

    for issue, articles in ISSUES:
        issue_doc_ids = {article_doc_id(article) for article in articles}
        selected_doc_ids = sorted(requested & issue_doc_ids)
        if requested and not selected_doc_ids:
            continue
        run_issue(issue, articles, selected_doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
