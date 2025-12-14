from fastapi import FastAPI
from app.api.visibility import router as visibility_router

app = FastAPI(title="Sky Visibility Service")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(visibility_router)

