from fastapi import FastAPI
from app.api.visibility import router as visibility_router
from app.api.cache import router as cache_router

app = FastAPI(title="Sky Visibility API")

# Include routers
app.include_router(visibility_router)
app.include_router(cache_router)

@app.get("/")
def read_root():
    return {"message": "Sky Visibility API is running"}

