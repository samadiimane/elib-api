from pydantic import BaseModel
from datetime import date

class JournalOut(BaseModel):
    id: int
    slug: str
    name: str
    issn: str | None = None
    publisher: str | None = None
    description: str | None = None

class JournalTranslationOut(BaseModel):
    locale: str
    title: str
    description: str | None = None
    publisher: str | None = None

class JournalCounts(BaseModel):
    issues: int
    documents: int

class JournalDetailOut(BaseModel):
    journal: JournalOut
    counts: JournalCounts

class JournalIssueOut(BaseModel):
    id: int
    volume: int | None = None
    number: int | None = None
    year: int | None = None
    title: str | None = None
    description: str | None = None
    issue_date: date | None = None

class IssueTranslationOut(BaseModel):
    locale: str
    title: str
    description: str | None = None
