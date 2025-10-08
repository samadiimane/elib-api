from fastapi import FastAPI
app = FastAPI(title="eLibrary API")

@app.get("/health")
def health():
    return {"status": "ok"}
