"""Seed Dar al-Niaba issue 07 as one whole-issue PDF document.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_07
    python -m scripts.seed_dar_al_niaba_issue_07 dar-al-niaba-07
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد السابع، السنة الثانية، صيف 1985",
    "year": 1985,
    "volume": 2,
    "number": 7,
}


ARTICLES = [
    {
        "title": "العدد الكامل: العدد السابع، السنة الثانية، صيف 1985",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": None,
        "start_page": None,
        "end_page": None,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-07.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
