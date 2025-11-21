from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.routes.categories import router as categories_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.api.routes.files import router as files_router
from app.api.routes.journals import router as journals_router
from app.api.routes.events import router as events_router
from app.api.routes.auth import router as auth_router
from app.api.routes.admin import router as admin_router
from app.api.routes.admin_capabilities import router as admin_capabilities_router
from app.api.routes.admin_categories import router as admin_categories_router
from app.api.routes.admin_authors import router as admin_authors_router
from app.api.routes.admin_journals import router as admin_journals_router, issue_router as admin_issue_router
from app.api.routes.uploads import router as uploads_router

app = FastAPI(title="eLibrary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(categories_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(files_router)
app.include_router(journals_router)
app.include_router(events_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(admin_capabilities_router)
app.include_router(admin_categories_router)
app.include_router(admin_authors_router)
app.include_router(admin_journals_router)
app.include_router(admin_issue_router)
app.include_router(uploads_router)
