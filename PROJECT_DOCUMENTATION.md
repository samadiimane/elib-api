# eLibrary API Project Documentation

Generated from the repository state in `d:\MSI\Fondation\elib-api`.

## 1. Project Overview

`elib-api` is a FastAPI backend for an e-library / foundation content platform. It exposes read APIs for documents, categories, journals, journal issues, events, search, file access, and authentication. It also exposes admin APIs for users, categories, authors, documents, journals, issues, upload presigning, and capability discovery.

The project uses SQLAlchemy 2 ORM, Alembic migrations, Pydantic v2 schemas, JWT authentication, bcrypt password hashing, and S3-compatible object storage for document files/uploads.

## 2. Repository Layout

```text
app/
  api/
    dependencies/        Auth dependencies for bearer tokens and role checks.
    routes/              FastAPI route modules.
  core/                  Runtime configuration.
  db/                    Engine, session factory, declarative base.
  models/                SQLAlchemy ORM models.
  repositories/          Data-access and domain mutation logic.
  schemas/               Pydantic request/response schemas.
  services/              Auth, search helpers, storage, localized categories.
migrations/              Alembic environment and revision files.
scripts/                 Local/dev seed and migration helper scripts.
tests/                   Pytest suite.
README.md                Short migration sanity-check notes.
requirements.txt         Python dependencies.
Dockerfile               Uvicorn container image.
dev.db                   Local SQLite database with sample data.
```

There is also a root `test_app.py` with a standalone `/ping` FastAPI app. It is not wired into `app.main`.

## 3. Tech Stack

- Web framework: FastAPI `~0.115`
- ASGI server: Uvicorn `~0.30`
- Validation/settings: Pydantic v2, pydantic-settings
- ORM/database: SQLAlchemy 2, Alembic
- Auth: PyJWT, passlib bcrypt, email-validator
- Storage: boto3 against S3-compatible endpoint such as MinIO
- Testing: pytest, httpx
- Production database driver: `psycopg2-binary` on non-Windows platforms
- Local default database: SQLite `dev.db`

## 4. Runtime Configuration

Configuration is defined in `app/core/config.py` via `Settings`. It reads `.env` and ignores unknown keys.

Supported environment variables:

- `DATABASE_URL`: defaults to `sqlite:///./dev.db`. Relative SQLite URLs are normalized to the repository root `dev.db`.
- `CORS_ORIGINS`: accepts JSON array or comma-separated string. Defaults to localhost frontend origins.
- `DEFAULT_LOCALE`: defaults to `en`.
- `STORAGE_ENDPOINT`: defaults to `http://127.0.0.1:9000`.
- `STORAGE_BUCKET`: defaults to `documents`.
- `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_REGION`.
- `STORAGE_CDN_BASE`: optional public URL base for uploads.
- `AUTH_SECRET`: JWT HMAC secret. The default is insecure and should be overridden.
- `ACCESS_TOKEN_EXP_MINUTES`: defaults to `60`.

The repository has a `.env` file with `DATABASE_URL`, `AUTH_SECRET`, `ACCESS_TOKEN_EXP_MINUTES`, and `CORS_ORIGINS`. Secret values are intentionally not documented here.

## 5. Application Entry Point

The active app is `app.main:app`.

It creates `FastAPI(title="eLibrary API")`, enables CORS from `settings.cors_origins`, exposes `GET /health`, and includes these route groups:

- categories
- documents
- search
- files
- journals
- events
- auth
- admin users
- admin capabilities
- admin categories
- admin authors
- admin documents
- admin journals and issues
- uploads

`app/api/routes/library.py` exists but is deprecated and is not included by `app.main`.

## 6. Database Model

### Active ORM Tables

`app.models` exports 15 ORM tables:

- `users`
- `auth_identities`
- `user_roles`
- `categories`
- `documents`
- `authors`
- `document_authors`
- `journals`
- `journal_issues`
- `journal_translations`
- `events`
- `seminar_events`
- `award_events`
- `exhibition_events`
- `award_event_winners`

The current local SQLite `dev.db` also contains Alembic-managed tables not exported by `app.models`: `alembic_version`, `category_translations`, `collections_legacy`, and `legacy_documents_legacy`.

### Enumerations

`CategoryKind`:

- `section`
- `journal`
- `archive_collection`
- `topic`

`DocumentType`:

- `book`
- `article`
- `thesis`
- `report`
- `manuscript`
- `archive_item`
- `site_record`
- `other`

`AuthProvider`:

- `password`
- `google`

`UserRoleEnum`:

- `researcher`
- `committee`
- `admin`

### Core Relationships

- A category can have a parent category and child categories.
- A category can link to a journal via `categories.journal_id`.
- A document can belong to one primary category.
- A document can link to a journal and optionally a journal issue.
- A document has ordered authors through `document_authors.position`.
- A journal has issues, documents, categories, and translations.
- An event has exactly one type-specific detail row for seminar, award, or exhibition where applicable.
- Award events can have ordered winners.
- A user has identities and roles.

### Soft Delete

Soft-delete columns exist on:

- `authors.deleted_at`
- `documents.deleted_at`
- `journals.deleted_at`

Public document and journal listings hide deleted rows. Admin listings can include `status=active|deleted|all`.

### Localization

Journals have an ORM model `JournalTranslation` and table `journal_translations` with unique `(journal_id, locale)`.

Categories use a table `category_translations`, but there is no ORM model for it. The code accesses it through a SQLAlchemy table literal in `app/repositories/categories.py`. Supported category locales are `en`, `fr`, `es`, and `ar`.

Category localization fallback is requested locale, then English translation, then base category fields. Journal localization fallback is requested locale, base locale variant, configured default locale, then base journal fields.

## 7. Domain Behavior

### Categories

Public category APIs support listing, detail, and immediate children. They can filter by kind, parent slug, search term, sort, pagination, and locale.

Admin category logic supports:

- Tree reads with configurable max depth.
- Children reads.
- Flat list with path fragments and document counts.
- Create with slug normalization.
- Update name/slug.
- Move between parents or to root.
- Reorder siblings.
- Delete only if there are no children and no documents.

Important invariants:

- Slugs are unique per `CategoryKind`.
- Parent and child categories must have the same `CategoryKind`.
- Moving a category into itself or descendants is blocked.
- Reorder payload must include all siblings.

### Documents

Documents include bibliographic fields, publication metadata, optional cover image URL, optional storage file key, journal/issue links, page ranges, primary category, and ordered authors.

Public document listing supports:

- `q` against title and abstract.
- `type`
- `lang`
- `year_min` and `year_max`
- `category_slug`
- sort by created date, year, or title.
- pagination.

Search adds:

- repeated `type` filters.
- repeated `lang` filters.
- `year_from` and `year_to`.
- `category`.
- `include_descendants`.
- `author`.
- facets for type, language, category, and decade year buckets.

If a category links to a journal, category filtering maps to `Document.journal_id` instead of `Document.primary_category_id`.

Admin document create/update enforces:

- title and language are required.
- issue id, if provided, must exist and forces `journal_id` to the issue journal.
- issue-linked documents are articles.
- journal category without issue also forces article.
- archive collection category forces `archive_item`.
- `historical-sites` category defaults to `site_record` when no type is provided.
- year must be between 1800 and 2100.
- end page cannot be before start page.
- pages are inferred from start/end page when absent.
- pages must be non-negative.
- author IDs are deduplicated and must exist as active authors.

The `Document` model also has a SQLAlchemy event listener that guarantees `Document.journal_id` matches the selected issue's journal.

### Authors

Authors store Arabic name, optional Latin name, affiliation, slug, timestamps, and soft-delete state.

Admin author behavior:

- list with search on Latin name.
- filter status: `active`, `deleted`, `all`.
- create from Latin name, optional Arabic name and affiliation.
- slug is generated from Latin name.
- duplicate slugs are rejected.
- soft delete and restore are supported.

### Journals and Issues

Journals store slug, name, ISSN, publisher, description, cover image URL, timestamps, soft-delete, issues, documents, linked categories, and translations.

Public journal behavior:

- list journals with `q`, `sort`, pagination, and locale.
- get detail with issue/document counts.
- list issues by year, volume, number, sort, pagination, and locale.
- list all articles for a journal.
- list articles for an issue.

Admin journal behavior:

- list by query, status, sort, pagination.
- counts issues and article documents.
- create/update with slug normalization.
- active journal slugs must be unique.
- soft delete and restore.

Admin issue behavior:

- list by journal, query, year, sort, pagination.
- create/update title, year, number, volume, publication date.
- year must be 1800 to 2100.
- number and volume must be non-negative.
- `(journal_id, year, number)` is unique when year and number are both present.
- delete is blocked if article documents are linked to the issue.

### Events

Events support three types:

- `seminar`
- `award`
- `exhibition`

Base event fields are slug, type, title, summary, body, dates, location, cover image, publication flag, order, and timestamps.

Type-specific data:

- Seminar: speakers, agenda, media JSON.
- Award: award year, discipline, notes, winners.
- Exhibition: venue, gallery JSON, curator.

Public event APIs return only published events. Detail serialization validates each type and returns type-specific `details`.

### Authentication and Users

Auth supports password accounts, placeholder Google auth, JWT access tokens, and role-based authorization.

Password behavior:

- Passwords are hashed with bcrypt.
- Passwords are truncated to bcrypt's 72-byte limit before hashing or verification.
- Signups default to the `researcher` role.

Google behavior:

- `validate_google_id_token` is currently a placeholder that accepts a JSON string containing `sub` and `email`.
- Google-created users default to `researcher`.
- Google identities are unique by `(provider, provider_user_id)`.

JWT behavior:

- HS256 tokens.
- Payload includes `sub`, `email`, `roles`, `iat`, and `exp`.
- Token secret comes from `AUTH_SECRET`.

Roles:

- `admin` has full admin APIs.
- `committee` can access admin capabilities and upload presign.
- `researcher` is the default user role.

Admin user behavior:

- list users with email search and role filter.
- create users with optional roles.
- replace user roles.
- activate/deactivate users.

### Storage and Uploads

`app/services/storage.py` creates a boto3 S3 client from settings. It supports:

- `object_exists(key)`
- `presigned_get_url(key, expires=3600)`

Public file route:

- `GET /v1/{document_id}/file`
- Uses `Document.file_key` when present, otherwise falls back to `/{document_id}.pdf`.
- Checks object existence before generating a one-hour GET URL.

Upload route:

- `POST /v1/uploads/presign`
- Requires `admin` or `committee`.
- Accepts `content_type`.
- Generates a random `uploads/{uuid}` object key.
- Returns PUT presigned URL, public URL, key, and content-type header.

## 8. API Surface

The active app exposes 54 custom routes, excluding FastAPI docs/OpenAPI routes.

### Public and Auth Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Health check. |
| GET | `/v1/categories` | List localized categories. |
| GET | `/v1/categories/{slug}` | Category detail plus document count. |
| GET | `/v1/categories/{slug}/children` | Immediate children, optionally with document counts. |
| GET | `/v1/documents` | List active documents. |
| GET | `/v1/documents/{document_id}` | Document detail. |
| GET | `/v1/search/documents` | Search documents with facets. |
| GET | `/v1/{document_id}/file` | Presigned document download URL. |
| GET | `/v1/journals` | List journals. |
| GET | `/v1/journals/{slug}` | Journal detail plus counts. |
| GET | `/v1/journals/{slug}/issues` | List journal issues. |
| GET | `/v1/journals/{slug}/articles` | List journal articles. |
| GET | `/v1/journals/{slug}/issues/{issue_id}/articles` | List issue articles. |
| GET | `/v1/events` | List published events. |
| GET | `/v1/events/{slug}` | Published event detail. |
| POST | `/v1/auth/signup` | Create password user. |
| POST | `/v1/auth/login` | Password login and JWT issue. |
| POST | `/v1/auth/google` | Placeholder Google login and JWT issue. |
| GET | `/v1/auth/me` | Current authenticated user. |
| POST | `/v1/auth/users/{user_id}/roles` | Admin-only role add. |
| DELETE | `/v1/auth/users/{user_id}/roles/{role}` | Admin-only role removal. |

### Admin Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/v1/admin/users` | List users. |
| POST | `/v1/admin/users` | Create admin-managed user. |
| PATCH | `/v1/admin/users/{user_id}/roles` | Replace user roles. |
| PATCH | `/v1/admin/users/{user_id}/active` | Activate/deactivate user. |
| GET | `/v1/admin/capabilities` | Static capability payload. |
| GET | `/v1/admin/categories/tree` | Category tree. |
| GET | `/v1/admin/categories/children/{parent_id}` | Category children. |
| GET | `/v1/admin/categories/list` | Flat category list. |
| POST | `/v1/admin/categories` | Create category. |
| PATCH | `/v1/admin/categories/reorder` | Reorder siblings. |
| DELETE | `/v1/admin/categories/{category_id}` | Delete category. |
| PATCH | `/v1/admin/categories/{category_id}` | Update category. |
| PATCH | `/v1/admin/categories/{category_id}/move` | Move category. |
| GET | `/v1/admin/authors` | List authors. |
| POST | `/v1/admin/authors` | Create author. |
| PATCH | `/v1/admin/authors/{author_id}/soft-delete` | Soft-delete author. |
| PATCH | `/v1/admin/authors/{author_id}/restore` | Restore author. |
| GET | `/v1/admin/documents` | List admin documents. |
| GET | `/v1/admin/documents/{document_id}` | Admin document detail. |
| POST | `/v1/admin/documents` | Create document. |
| PATCH | `/v1/admin/documents/{document_id}` | Update document. |
| PATCH | `/v1/admin/documents/{document_id}/delete` | Soft-delete document. |
| PATCH | `/v1/admin/documents/{document_id}/restore` | Restore document. |
| GET | `/v1/admin/journals` | List journals. |
| POST | `/v1/admin/journals` | Create journal. |
| PATCH | `/v1/admin/journals/{journal_id}` | Update journal. |
| PATCH | `/v1/admin/journals/{journal_id}/soft-delete` | Soft-delete journal. |
| PATCH | `/v1/admin/journals/{journal_id}/restore` | Restore journal. |
| GET | `/v1/admin/journals/{journal_id}/issues` | List journal issues. |
| POST | `/v1/admin/journals/{journal_id}/issues` | Create journal issue. |
| PATCH | `/v1/admin/issues/{issue_id}` | Update issue. |
| DELETE | `/v1/admin/issues/{issue_id}` | Delete issue. |
| POST | `/v1/uploads/presign` | Presign S3-compatible upload. |

## 9. Response Schemas

Common paginated response:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "has_next": false
}
```

Primary schema groups:

- `category.py`: category list/detail/children payloads and linked journal references.
- `document.py`: public document response with authors and primary category.
- `search.py`: document search response with facets.
- `journal.py`: public journal, issue, counts, detail.
- `event.py`: event list/detail and type-specific detail unions.
- `user.py`: auth, user, role, admin user payloads.
- `admin_*`: admin category, author, document, journal, issue payloads.

## 10. Migrations

Alembic is configured in `alembic.ini` and `migrations/env.py`. The migration environment imports `app.models` to populate SQLAlchemy metadata.

Current migration head:

```text
20260105_000016
```

The local `dev.db` is also at head.

Major migration history:

- Initial legacy collections/documents.
- New categories and documents.
- Legacy table rename/cleanup.
- PostgreSQL trigram indexes for document search.
- Journals and journal issues.
- Category to journal links and backfill.
- Authors and document cover image support.
- Event tables.
- Auth tables.
- Admin category metadata.
- Author indexes and soft delete.
- Journal soft delete, cover image, and indexes.
- Journal issue composite indexes.
- Admin document indexes.
- Document `file_key`.
- Document soft delete.
- Journal translations.
- Temporary issue translations, later dropped.
- Default-locale translation backfill.
- Category translations.

## 11. Seed Scripts

The `scripts/` folder contains local/dev data setup:

- `dev_init_db.py`: creates tables directly from SQLAlchemy metadata.
- `dev_seed_basic.py`: base document/category/author seed data.
- `dev_seed_categories.py`: category hierarchy seed data.
- `dev_seed_archives.py`: archive collection documents and categories.
- `dev_seed_publications.py`: publication documents and categories.
- `dev_seed_research_themes.py`: research theme data.
- `dev_seed_sites.py`: historical site records.
- `dev_seed_journals.py`: journal, issue, and article data.
- `dev_seed_dar_al_niaba.py`: Dar al-Niaba journal-specific seed data.
- `dev_seed_events.py`: seminar, award, and exhibition examples.
- `seed_real_data.py`: bundled realistic category/journal/article seed.
- `seed_translations.py`: journal translation upserts.
- `seed_category_translations.py`: category translation upserts.

Several translation seed literals show mojibake in the file output, so verify encoding before relying on seeded Arabic/French/Spanish copy in production.

## 12. Local Database Snapshot

The checked local `dev.db` currently contains:

| Table | Rows |
| --- | ---: |
| `categories` | 17 |
| `category_translations` | 41 |
| `documents` | 56 |
| `authors` | 12 |
| `document_authors` | 102 |
| `journals` | 7 |
| `journal_issues` | 11 |
| `journal_translations` | 28 |
| `events` | 4 |
| `users` | 16 |
| `auth_identities` | 16 |
| `user_roles` | 16 |
| `collections_legacy` | 0 |
| `legacy_documents_legacy` | 0 |

## 13. Tests

The suite has 52 tests across 20 test files. It covers:

- Alembic migrations.
- Category tree, children, locale behavior, linked journal behavior.
- Document listing, admin create/update/delete/restore, issue invariants.
- Search by author, category, descendants, facets.
- Admin users, roles, capabilities.
- Admin authors.
- Admin journals and issues.
- Events API and type-specific serialization.
- Query-count checks for selected repository methods.

Latest run:

```text
50 passed, 2 failed, 50 warnings
```

Failing tests:

- `tests/test_categories_api_linked_journal.py::test_categories_api_includes_linked_journal_block`
  - Expected `/v1/categories` items to include `linked_journal`, but current list response uses `CategoryLocalizedOut`, which has `journal_id` but no `linked_journal`.
- `tests/test_categories_locale_api.py::test_list_children_returns_translated_name`
  - Fails in the test before the request because `parent.slug` is accessed after the SQLAlchemy session is closed, producing `DetachedInstanceError`.

Warnings:

- `pydantic.generics.GenericModel` import is deprecated in Pydantic v2.
- `Session.close_all()` is deprecated in SQLAlchemy.

## 14. Operational Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
alembic upgrade head
```

Run app locally:

```bash
uvicorn app.main:app --reload
```

Run tests with the repository virtual environment on Windows:

```bash
.\.venv\Scripts\pytest.exe -q
```

Build Docker image:

```bash
docker build -t elib-api .
```

Run container:

```bash
docker run -p 8000:8000 --env-file .env elib-api
```

## 15. Deployment Notes

The Dockerfile uses `python:3.11-slim`, installs `requirements.txt`, copies app, migrations, and scripts, exposes port 8000, and starts:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The container does not run migrations automatically. Deployments need a separate `alembic upgrade head` step.

For production, use a strong `AUTH_SECRET`, a production `DATABASE_URL`, and real S3-compatible storage credentials.

## 16. Known Gaps and Risks

- The current test suite is not green.
- Public category list does not currently include `linked_journal`, despite a test expecting it.
- One category locale test has a fixture/session-lifetime bug.
- `validate_google_id_token` is explicitly a placeholder and does not verify Google signatures.
- `category_translations` has no ORM model even though it is used by repository logic.
- `library.py` contains deprecated legacy endpoints, but they are not mounted.
- `test_app.py` is a separate sample FastAPI app and not part of the production API.
- The default `AUTH_SECRET` is insecure if `.env` is absent.
- Migrations include PostgreSQL trigram index creation while local development is SQLite.
- Some seed translation files appear to contain mojibake text.
