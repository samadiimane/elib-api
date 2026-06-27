"""Seed Dar al-Niaba combined issue 26 / 27 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_26
    python -m scripts.seed_dar_al_niaba_issue_26 dar-al-niaba-26-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العددان 26 / 27، السنة السابعة، ربيع / صيف 1990",
    "year": 1990,
    "volume": 7,
    "number": 26,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 6,
        "start_page": 1,
        "end_page": 4,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-1.pdf",
    },
    {
        "title": 'أضواء على "رسالة" محمد صادق العطار الشامي الصادرة بطنجة عام 1901',
        "authors": ["أحمد المكّاوي"],
        "lang": "ar",
        "pages": 9,
        "start_page": 5,
        "end_page": 13,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-2.pdf",
    },
    {
        "title": "أضواء على العمل الوطني بمكناس خلال الحرب العالمية الأولى",
        "authors": ["محمد بكراوي"],
        "lang": "ar",
        "pages": 6,
        "start_page": 14,
        "end_page": 19,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-3.pdf",
    },
    {
        "title": "أرشيف وزارة الخارجية الفرنسية : رسائل سلطانية جديدة المجموعة الأولى",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 20,
        "end_page": 22,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-4.pdf",
    },
    {
        "title": "المغرب وإسبانيا عند نهاية القرن الثامن عشر معاهدة فاتح مارس 1799",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 23,
        "end_page": 25,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-5.pdf",
    },
    {
        "title": "مراسلات الوكيل القنصلي الفرنسي بالقصر الكبير في العهد الحسني",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 8,
        "start_page": 26,
        "end_page": 33,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-6.pdf",
    },
    {
        "title": "أوبئة ومجاعات المغرب في القرنين الثامن عشر والتاسع عشر",
        "authors": ["محمد الأمين البزاز", "عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 6,
        "start_page": 34,
        "end_page": 39,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-7.pdf",
    },
    {
        "title": "المغرب الأقصى في عهد السلطان الحسن الاول",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 40,
        "end_page": 42,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-8.pdf",
    },
    {
        "title": "العلاقات الالمانية الفرنسية والشؤون المغربية (1901 - 1911)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 8,
        "start_page": 43,
        "end_page": 50,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-9.pdf",
    },
    {
        "title": "(1965-1875)الفقيه محمد سكيرج",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 5,
        "start_page": 51,
        "end_page": 55,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-10.pdf",
    },
    {
        "title": "وثيقة جديدة حول الهجوم على تازروت وأسر القائد أحمد الريسوني (يناير 1925)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 7,
        "start_page": 56,
        "end_page": 62,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-26-11.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
