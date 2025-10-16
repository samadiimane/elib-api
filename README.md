# eLibrary API

## Coherence Check (Step 1.5)

```bash
# 1) Migrations
alembic upgrade head

# 2) DB tables: legacy tables are renamed (if they existed)
#    Expect: collections_legacy, legacy_documents_legacy (or not present if never existed)
psql -U postgres -d elib -c "\dt"

# 3) App routes
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/v1/categories
curl "http://127.0.0.1:8000/v1/documents?page=1&page_size=10"

# 4) Code search: no public imports of legacy models
# (Windows PowerShell)
Get-ChildItem -Recurse app | Select-String -Pattern "\bCollection\b|\bLegacyDocument\b" |
  Select-Object Path, LineNumber, Line
```

---
