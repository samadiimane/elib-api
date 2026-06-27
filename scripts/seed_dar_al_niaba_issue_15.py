"""Seed Dar al-Niaba combined issue 15 / 16 as one whole-issue PDF document.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_15
    python -m scripts.seed_dar_al_niaba_issue_15 dar-al-niaba-15-16
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العددان 15 / 16، السنة الرابعة، صيف / خريف 1987",
    "year": 1987,
    "volume": 4,
    "number": 15,
}


ARTICLES = [
    {
        "title": "العدد الكامل: العددان 15 / 16، السنة الرابعة، صيف / خريف 1987",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": None,
        "start_page": None,
        "end_page": None,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-15-16.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
