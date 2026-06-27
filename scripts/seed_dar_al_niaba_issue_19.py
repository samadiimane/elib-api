"""Seed Dar al-Niaba combined issue 19 / 20 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_19
    python -m scripts.seed_dar_al_niaba_issue_19 dar-al-niaba-19-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العددان 19 / 20، السنة الخامسة، صيف / خريف 1988",
    "year": 1988,
    "volume": 5,
    "number": 19,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 4,
        "start_page": 1,
        "end_page": 2,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-1.pdf",
    },
    {
        "title": "المخطوطات العربية في الغرب الاسلامي: وضعية المجموعات وآفاق البحث",
        "authors": [],
        "lang": "ar",
        "pages": 7,
        "start_page": 3,
        "end_page": 9,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-2.pdf",
    },
    {
        "title": "سياسة ابريطانيا العظمى حيال الدولة العثمانية والدولة المغربية خلال القرن التاسع عشر",
        "authors": ["إبراهيم بوطالب"],
        "lang": "ar",
        "pages": 16,
        "start_page": 10,
        "end_page": 25,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-3.pdf",
    },
    {
        "title": "شخصيات مجددة في مغرب القرن التاسع عشر",
        "authors": ["محمد المنوني"],
        "lang": "ar",
        "pages": 4,
        "start_page": 26,
        "end_page": 29,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-4.pdf",
    },
    {
        "title": "حول مسألة بناء الملاّحات بالمدن المغربية",
        "authors": ["عبد العزيز الخمليشي"],
        "lang": "ar",
        "pages": 12,
        "start_page": 30,
        "end_page": 41,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-5.pdf",
    },
    {
        "title": "قضايا شمال إفريقيا من خلال مجلة «مغرب» الباريسية (1932 - 1935)",
        "authors": ["جامع بيضا"],
        "lang": "ar",
        "pages": 6,
        "start_page": 42,
        "end_page": 47,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-6.pdf",
    },
    {
        "title": "موقف الرأي العام المغربي من خلال الفتاوى الشرعية في القرن التاسع عشر وبداية العشرين",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 10,
        "start_page": 48,
        "end_page": 57,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-7.pdf",
    },
    {
        "title": "وثائق مغربية حول القبائل المجاورة لسبتة (1892-1911)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 10,
        "start_page": 58,
        "end_page": 67,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-19-8.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
