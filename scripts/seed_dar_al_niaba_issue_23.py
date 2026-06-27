"""Seed Dar al-Niaba combined issue 23 / 24 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_23
    python -m scripts.seed_dar_al_niaba_issue_23 dar-al-niaba-23-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العددان 23 / 24، السنة السادسة، صيف / خريف 1989",
    "year": 1989,
    "volume": 6,
    "number": 23,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 12,
        "start_page": 1,
        "end_page": 10,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-1.pdf",
    },
    {
        "title": "الرؤية الخلدونية للحضارة الأندلسية",
        "authors": ["محمد رزوق"],
        "lang": "ar",
        "pages": 7,
        "start_page": 11,
        "end_page": 17,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-2.pdf",
    },
    {
        "title": "مظاهر الرأسمالية الزراعية في مغرب ما قبل الحماية - القسم الثاني",
        "authors": ["كركوري لازارف", "أبو بكر العشاب"],
        "lang": "ar",
        "pages": 17,
        "start_page": 18,
        "end_page": 34,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-3.pdf",
    },
    {
        "title": "الحركة الوطنية المغربية من خلال الأرشيف الفوتوغرافي الإسباني بمدريد",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 5,
        "start_page": 35,
        "end_page": 39,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-4.pdf",
    },
    {
        "title": "وحدة النضال في المغرب العربي من خلال الصحافة في المنطقة الشمالية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 40,
        "end_page": 43,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-5.pdf",
    },
    {
        "title": "الحركة الريسونية من خلال الوثائق القنصلية الأجنبية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 8,
        "start_page": 44,
        "end_page": 51,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-6.pdf",
    },
    {
        "title": "اتفاقية 5 مارس 1894 بين المغرب واسبانيا",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 60,
        "end_page": 62,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-8.pdf",
    },
    {
        "title": "فرنسا في المغرب",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 63,
        "end_page": 64,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-9.pdf",
    },
    {
        "title": "رسائل غير منشورة حول حرب الريف التحريرية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 7,
        "start_page": 65,
        "end_page": 71,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-10.pdf",
    },
    {
        "title": "من مراسلات جبالة مع محمد بن عبد الكريم الخطابي",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 7,
        "start_page": 72,
        "end_page": 78,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-11.pdf",
    },
    {
        "title": "قراءة في كتاب جرمان عياش أصول حرب الريف (1909 - 1921)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 6,
        "start_page": 79,
        "end_page": 84,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-12.pdf",
    },
    {
        "title": "وثائق مغربية حول حركة التهريب بقبيلة بقيوة سنة 1898",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 8,
        "start_page": 85,
        "end_page": 92,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-23-13.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
