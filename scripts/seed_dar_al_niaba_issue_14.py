"""Seed Dar al-Niaba issue 14 as one whole-issue PDF document.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_14
    python -m scripts.seed_dar_al_niaba_issue_14 dar-al-niaba-14
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد الرابع عشر، السنة الرابعة، ربيع 1987",
    "year": 1987,
    "volume": 4,
    "number": 14,
}


ARTICLES = [
    {
        "title": "العدد الكامل: العدد الرابع عشر، السنة الرابعة، ربيع 1987",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": None,
        "start_page": None,
        "end_page": None,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-14.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
