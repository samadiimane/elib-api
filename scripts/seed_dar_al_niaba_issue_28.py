"""Seed Dar al-Niaba issue 28 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_28
    python -m scripts.seed_dar_al_niaba_issue_28 dar-al-niaba-28-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد 28، السنة الثامنة، 1991",
    "year": 1991,
    "volume": 8,
    "number": 28,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 5,
        "start_page": 1,
        "end_page": 4,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-1.pdf",
    },
    {
        "title": "جذور حرب الريف",
        "authors": ["سيمون ليفي", "أبو بكر العشاب"],
        "lang": "ar",
        "pages": 12,
        "start_page": 5,
        "end_page": 16,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-2.pdf",
    },
    {
        "title": "العلاقات بين القبائل والمخزن في القرن 19 من منظور جرمان عياش",
        "authors": ["محمد الأمين البزاز"],
        "lang": "ar",
        "pages": 4,
        "start_page": 17,
        "end_page": 20,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-3.pdf",
    },
    {
        "title": "الحركة الريسونية من خلال كتابات جرمان عياش",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 21,
        "end_page": 23,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-4.pdf",
    },
    {
        "title": "دراسات في تاريخ المغرب للفقيد جرمان عياش",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 24,
        "end_page": 26,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-5.pdf",
    },
    {
        "title": "طنجة في بداية القرن التاسع عشر من خلال رحلة علي باي العباسي",
        "authors": ["عبد العزيز الخمليشي"],
        "lang": "ar",
        "pages": 11,
        "start_page": 27,
        "end_page": 37,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-6.pdf",
    },
    {
        "title": "مقاومة أهالي تافيلالت والاستطوغرافيا الاستعمارية (1914-1934)",
        "authors": ["بوراس عبد القادر"],
        "lang": "ar",
        "pages": 7,
        "start_page": 38,
        "end_page": 44,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-7.pdf",
    },
    {
        "title": "أحداث مليلية في خريف 1893",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 45,
        "end_page": 48,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-8.pdf",
    },
    {
        "title": "المجتمع الفحصي في القرن التاسع عشر",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 49,
        "end_page": 52,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-9.pdf",
    },
    {
        "title": "حول علاقات المدينة المغربية بأحوازها في بداية القرن العشرين مثال حصار جبالة لتطوان 1903-1904",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 53,
        "end_page": 56,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-10.pdf",
    },
    {
        "title": "جوانب من الحياة الاجتماعية والعلمية بتطوان في القرن التاسع عشر",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 57,
        "end_page": 58,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-11.pdf",
    },
    {
        "title": "عرض حول كتاب الاستاذ المختار الهراس : القبيلة والسلطة : تطوان الهياكل القبيلية شمال غرب المغرب",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 59,
        "end_page": 62,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-12.pdf",
    },
    {
        "title": "التدخل الأجنبي والمقاومة بالمغرب (1894-1910) حادثة الدار البيضاء واحتلال الشاوية",
        "authors": ["علال الخديمي", "عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 63,
        "end_page": 65,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-13.pdf",
    },
    {
        "title": "كتابات ما قبل عهد الاستقلال",
        "authors": ["جرمان عياش", "عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 66,
        "end_page": 67,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-14.pdf",
    },
    {
        "title": "جوانب من الأعمال الاجتماعية لمولى الحسن الأول بطنجة",
        "authors": ["محمد الأمين البزاز"],
        "lang": "ar",
        "pages": 6,
        "start_page": 68,
        "end_page": 73,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-15.pdf",
    },
    {
        "title": "زيارة غليوم الثاني لطنجة من خلال الوثائق المغربية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 74,
        "end_page": 77,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-16.pdf",
    },
    {
        "title": "رسالة جامعية مغربية بباريس في موضوع : القطب الشهيد مولاي عبد السلام بن مشيش",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 78,
        "end_page": 80,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-17.pdf",
    },
    {
        "title": "فضاء الروائي عبد القادر الشط : طنجة العتيقة وأحوازها",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 81,
        "end_page": 82,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-18.pdf",
    },
    {
        "title": "تاريخ الزلازل بالمغرب",
        "authors": ["ثريا المرابط أزروال", "عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 83,
        "end_page": 84,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-19.pdf",
    },
    {
        "title": "مساهمة طنجة في الحركة الوطنية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 8,
        "start_page": 85,
        "end_page": 92,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-28-20.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
