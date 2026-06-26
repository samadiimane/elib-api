"""Seed Dar al-Niaba issue 21 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_21
    python -m scripts.seed_dar_al_niaba_issue_21 dar-al-niaba-21-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد 21، السنة السادسة، شتاء 1989",
    "year": 1989,
    "volume": 6,
    "number": 21,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 6,
        "start_page": 1,
        "end_page": 3,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-1.pdf",
    },
    {
        "title": "وثائق مغربية من القرن 19",
        "authors": ["محمد المنوني"],
        "lang": "ar",
        "pages": 7,
        "start_page": 4,
        "end_page": 10,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-2.pdf",
    },
    {
        "title": "سياسة ابريطانية العظمى حيال الدولة العثمانية والدولة المغربية خلال القرن التاسع عشر",
        "authors": ["إبراهيم بوطالب"],
        "lang": "ar",
        "pages": 2,
        "start_page": 11,
        "end_page": 12,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-3.pdf",
    },
    {
        "title": "في توقير واحترام شيوخ الزاوية البوعمرية بمراكش",
        "authors": ["حسن جلاب"],
        "lang": "ar",
        "pages": 10,
        "start_page": 13,
        "end_page": 22,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-4.pdf",
    },
    {
        "title": "مخطوط نوازل ابن الحاج وأهمية مادته التاريخية",
        "authors": ["إبراهيم القادري بوتشيش"],
        "lang": "ar",
        "pages": 6,
        "start_page": 23,
        "end_page": 28,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-5.pdf",
    },
    {
        "title": "الزاوية الوزانية والمخزن خلال النصف الثاني من القرن الثامن عشر",
        "authors": ["فاطمة الحراق"],
        "lang": "ar",
        "pages": 5,
        "start_page": 29,
        "end_page": 33,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-6.pdf",
    },
    {
        "title": "موقف بريطانيا العظمى من الأطماع الإسبانية شمال المغرب خلال سنة 1859",
        "authors": ["خالد بن الصغير"],
        "lang": "ar",
        "pages": 10,
        "start_page": 34,
        "end_page": 43,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-7.pdf",
    },
    {
        "title": "مظاهر التدخل الفرنسي شمال المغرب الشرقي",
        "authors": ["عكاشة برحاب"],
        "lang": "ar",
        "pages": 8,
        "start_page": 44,
        "end_page": 51,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-8.pdf",
    },
    {
        "title": "مظاهر الرأسمالية الزراعية في مغرب ما قبل الحماية",
        "authors": ["كركوري لازارف", "أبو بكر العشاب"],
        "lang": "ar",
        "pages": 3,
        "start_page": 52,
        "end_page": 54,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-9.pdf",
    },
    {
        "title": "علاقة مدينة مكناس بباديتها - العلاقة السياسية والعسكرية - 1907 - 1918",
        "authors": ["بوشّتى بوعسرية"],
        "lang": "ar",
        "pages": 8,
        "start_page": 55,
        "end_page": 62,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-10.pdf",
    },
    {
        "title": "حول ربائد دار النيابة السعيدة بطنجة",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 6,
        "start_page": 63,
        "end_page": 68,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-11.pdf",
    },
    {
        "title": "آراء في الحركة الوطنية بالمغرب الشمالي",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 5,
        "start_page": 69,
        "end_page": 73,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-12.pdf",
    },
    {
        "title": "التنظيمات الاقتصادية والاجتماعية ببلاد جبالة من خلال الوثائق العدلية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 74,
        "end_page": 77,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-13.pdf",
    },
    {
        "title": "الحركة الريسونية من خلال الصحافة العربية والأجنبية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 5,
        "start_page": 78,
        "end_page": 82,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-21-14.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
