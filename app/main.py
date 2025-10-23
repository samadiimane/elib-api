from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.routes.categories import router as categories_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.api.routes.files import router as files_router
from app.api.routes.journals import router as journals_router

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
