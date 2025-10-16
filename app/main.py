from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.categories import router as categories_router
from app.api.routes.documents import router as documents_router
# from app.api.routes.library import router as library_router  # TODO: remove legacy route once clients migrate

app = FastAPI(title="eLibrary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(categories_router)
app.include_router(documents_router)
# app.include_router(library_router)  # TODO: drop before removing legacy endpoints
