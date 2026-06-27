"""Seed Dar al-Niaba issue 09 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_09
    python -m scripts.seed_dar_al_niaba_issue_09 dar-al-niaba-09-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد التاسع، السنة الثالثة، شتاء 1986",
    "year": 1986,
    "volume": 3,
    "number": 9,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 5,
        "start_page": 1,
        "end_page": 4,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-1.pdf",
    },
    {
        "title": "تقرير حول رسالة جامعية : حادثة الدار البيضاء واحتلال الشاوية (1907 - 1908) للأستاذ علال الخديمي",
        "authors": ["جرمان عياش"],
        "lang": "ar",
        "pages": 5,
        "start_page": 5,
        "end_page": 9,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-2.pdf",
    },
    {
        "title": "محمد الخامس: عرش وثلاث جمهوريات",
        "authors": ["جان ماري لاكوتور", "مصطفى بوشعراء"],
        "lang": "ar",
        "pages": 12,
        "start_page": 10,
        "end_page": 21,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-3.pdf",
    },
    {
        "title": "عوائد من «مدينة البوغاز»",
        "authors": ["عبد الغني سكيرج"],
        "lang": "ar",
        "pages": 3,
        "start_page": 22,
        "end_page": 24,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-4.pdf",
    },
    {
        "title": "إسهام مليلة في التجارة الصحراوية إلى بداية القرن الرابع الهجري",
        "authors": ["حسن الفكيكي"],
        "lang": "ar",
        "pages": 9,
        "start_page": 25,
        "end_page": 33,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-5.pdf",
    },
    {
        "title": "التنظيم الجماعي القروي: الطرق",
        "authors": ["المريني العياشي"],
        "lang": "ar",
        "pages": 3,
        "start_page": 34,
        "end_page": 36,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-6.pdf",
    },
    {
        "title": 'ظاهرة "السيبة" في مغرب القرن التاسع عشر',
        "authors": ["نور الدين سعودي"],
        "lang": "ar",
        "pages": 9,
        "start_page": 37,
        "end_page": 45,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-7.pdf",
    },
    {
        "title": "أسماء مغمورة لقادة الجهاد في المغرب: القائد أحمد اخريرو الحزمري (1898-1926)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 3,
        "start_page": 46,
        "end_page": 48,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-8.pdf",
    },
    {
        "title": "حياة القاضي أحمد سكيرج وآثاره",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 9,
        "start_page": 49,
        "end_page": 57,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-9.pdf",
    },
    {
        "title": "مذكرات محمد أزرقان عن حرب الريف: «الظل الوريق في محاربة الريف»",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 12,
        "start_page": 58,
        "end_page": 70,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-10.pdf",
    },
    {
        "title": "وثائق حول الفقيه الهاشمي بن العربي الشريف اليحمدي الفحصي",
        "authors": ["أحمد الفحصي"],
        "lang": "ar",
        "pages": 2,
        "start_page": 71,
        "end_page": 72,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-11.pdf",
    },
    {
        "title": "فتوى محمد بن جعفر الكتاني حول منع الحج سنة 1897",
        "authors": ["محمد بن جعفر الكتاني"],
        "lang": "ar",
        "pages": 2,
        "start_page": 73,
        "end_page": 74,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-12.pdf",
    },
    {
        "title": "حول الحج المغربي إلى الديار المقدسة في القرن التاسع عشر وبداية العشرين",
        "authors": ["محمد الأمين البزاز"],
        "lang": "ar",
        "pages": 13,
        "start_page": 75,
        "end_page": 87,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-09-13.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
