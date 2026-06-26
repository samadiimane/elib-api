"""Seed Dar al-Niaba issue 25 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_25
    python -m scripts.seed_dar_al_niaba_issue_25 dar-al-niaba-25-2
"""

from __future__ import annotations

import sys

from scripts.dar_al_niaba_seed_common import run_issue


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد 25، السنة السابعة، شتاء 1990",
    "year": 1990,
    "volume": 7,
    "number": 25,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 4,
        "start_page": 1,
        "end_page": 1,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-1.pdf",
    },
    {
        "title": "عبد الله كنون : أديباً ناقداً مؤرخاً ومحققاً للمخطوطات وناشراً",
        "authors": ["محمد المنوني"],
        "lang": "ar",
        "pages": 2,
        "start_page": 2,
        "end_page": 3,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-2.pdf",
    },
    {
        "title": "وثائق أرشيفية جديدة عن المرحوم عبد الله كنون : طنجة كمركز للعمل الاصلاحي والنشاط السياسي",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 5,
        "start_page": 4,
        "end_page": 8,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-3.pdf",
    },
    {
        "title": "\"النبوغ المغربي\" في منظور سوسيولوجي",
        "authors": ["عثمان أشقرا"],
        "lang": "ar",
        "pages": 2,
        "start_page": 9,
        "end_page": 10,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-4.pdf",
    },
    {
        "title": "تقرير حول رسالة الأستاذ عبد العزيز الخمليشي: جوانب من الحياة التجارية بالمغرب في القرن التاسع عشر (1856 - 1896):",
        "authors": ["جرمان عياش"],
        "lang": "ar",
        "pages": 4,
        "start_page": 11,
        "end_page": 14,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-5.pdf",
    },
    {
        "title": "جوانب من الحياة التجارية بالمغرب في القرن التاسع عشر (1856 - 1896): المخزن والضرائب المفروضة على التجارة الداخلية (مكوس الحواضر)",
        "authors": ["عبد العزيز الخمليشي"],
        "lang": "ar",
        "pages": 5,
        "start_page": 15,
        "end_page": 19,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-6.pdf",
    },
    {
        "title": "جوانب من الحياة التجارية بالمغرب في القرن التاسع عشر 1856 - 1896",
        "authors": ["عبد العزيز الخمليشي", "عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 20,
        "end_page": 23,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-7.pdf",
    },
    {
        "title": "مظاهر الرأسمالية الزراعية في مغرب ما قبل الحماية : القسم الثالث",
        "authors": ["كركوري لازارف", "أبو بكر العشاب"],
        "lang": "ar",
        "pages": 11,
        "start_page": 24,
        "end_page": 34,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-8.pdf",
    },
    {
        "title": "البرازيل وسياسة الحمايات",
        "authors": ["محمد العربي المساري"],
        "lang": "ar",
        "pages": 6,
        "start_page": 35,
        "end_page": 40,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-9.pdf",
    },
    {
        "title": "مداخيل الدولة على عهد السلطان سيدي محمد بن عبد الله",
        "authors": ["فاطمة الحراق"],
        "lang": "ar",
        "pages": 8,
        "start_page": 41,
        "end_page": 48,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-10.pdf",
    },
    {
        "title": "المغرب والعالم الخارجي في النصف الثاني من القرن الثامن عشر",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 49,
        "end_page": 50,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-11.pdf",
    },
    {
        "title": "حرب تطوان من خلال الأجوبة الفقهية (جواب أحمد المرنيسي نموذجا)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 51,
        "end_page": 54,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-12.pdf",
    },
    {
        "title": "المقاومة المسلحة في شمال المغرب",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 55,
        "end_page": 58,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-13.pdf",
    },
    {
        "title": "المغرب والحرب الأهلية الاسبانية",
        "authors": ["بوبكر بوهادي", "عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 59,
        "end_page": 62,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-14.pdf",
    },
    {
        "title": "العمل الوطني بشمال المغرب من خلال الوثائق الدبلوماسية الفرنسية",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 63,
        "end_page": 66,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-25-15.pdf",
    },
]


def run(doc_ids=()) -> None:
    run_issue(ISSUE, ARTICLES, doc_ids)


if __name__ == "__main__":
    run(sys.argv[1:])
