from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.library import router as library_router

app = FastAPI(title="eLibrary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health(): return {"status":"ok"}

app.include_router(library_router)
