from fastapi import FastAPI
from app.api.visibility import router
from app.api.cache import router as cache_router

app = FastAPI(title="Sky Visibility API")

app.include_router(router)
app.include_router(cache_router)

@app.get("/")
def read_root():
    return {"message": "Sky Visibility API is running"}

