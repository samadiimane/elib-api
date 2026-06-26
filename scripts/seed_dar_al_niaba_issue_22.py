"""Seed Dar al-Niaba issue 22 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_22
    python -m scripts.seed_dar_al_niaba_issue_22 dar-al-niaba-22-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد 22، السنة السادسة، ربيع 1989",
    "year": 1989,
    "volume": 6,
    "number": 22,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 17,
        "start_page": 1,
        "end_page": 17,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-1.pdf",
    },
    {
        "title": "إسهام الزاوية الناصرية في ربط الصلات بين بلدان الشمال الافريقي خلال القرنين 11/12 هـ - 17/18 م",
        "authors": ["أحمد عمالك"],
        "lang": "ar",
        "pages": 10,
        "start_page": 18,
        "end_page": 27,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-2.pdf",
    },
    {
        "title": "العلاقات التجارية بين المغرب وأوربا في النصف الثاني من القرن الثامن عشر",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 28,
        "end_page": 31,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-3.pdf",
    },
    {
        "title": "رحلة الغيغاني",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 5,
        "start_page": 32,
        "end_page": 36,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-4.pdf",
    },
    {
        "title": "بيبليوغرافيا عامة عن السلطان مولاي الحسن الاول",
        "authors": ["عبد المجيد بن يوسف"],
        "lang": "ar",
        "pages": 4,
        "start_page": 37,
        "end_page": 40,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-5.pdf",
    },
    {
        "title": "جلالة السلطان مولاي الحسن الأول",
        "authors": ["الدكتور محمد التهامي الوكيلي"],
        "lang": "ar",
        "pages": 13,
        "start_page": 41,
        "end_page": 51,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-6.pdf",
    },
    {
        "title": "أوضاع نظما ونثرا تصف رحلات السلطان الحسن الاول لتفقد جهات المغرب",
        "authors": ["محمد المنوني"],
        "lang": "ar",
        "pages": 2,
        "start_page": 52,
        "end_page": 53,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-7.pdf",
    },
    {
        "title": "البعثة العسكرية الفرنسية ودورها في تركيز النفوذ الفرنسي بالمغرب 1877 - 1912 دراسة من خلال وثائق الوزارة الحربية الفرنسية",
        "authors": ["حمان عبد الحفيظ"],
        "lang": "ar",
        "pages": 6,
        "start_page": 54,
        "end_page": 59,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-8.pdf",
    },
    {
        "title": "أضواء على العلاقات المغربية - البلجيكية في القرن التاسع عشر وبداية القرن العشرين",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 60,
        "end_page": 63,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-9.pdf",
    },
    {
        "title": "وثائق مغربية جديدة حول علاقة طنجة بأحوازها في العهد الحسني (1876 - 1892)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 6,
        "start_page": 64,
        "end_page": 69,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-10.pdf",
    },
    {
        "title": "قدوم السلطان مولاي الحسن لتطوان عام 1307 هـ",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 70,
        "end_page": 72,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-11.pdf",
    },
    {
        "title": "تسلط الأجانب والمحميين على العقارات في مغرب القرن التاسع عشر",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 73,
        "end_page": 76,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-22-12.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
