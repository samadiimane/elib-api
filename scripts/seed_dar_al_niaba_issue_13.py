"""Seed Dar al-Niaba issue 13 as one whole-issue PDF document.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_13
    python -m scripts.seed_dar_al_niaba_issue_13 dar-al-niaba-13
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد الثالث عشر، السنة الرابعة، شتاء 1987",
    "year": 1987,
    "volume": 4,
    "number": 13,
}


ARTICLES = [
    {
        "title": "العدد الكامل: العدد الثالث عشر، السنة الرابعة، شتاء 1987",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": None,
        "start_page": None,
        "end_page": None,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-13.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
