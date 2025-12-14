from fastapi import FastAPI

app = FastAPI(title="Sky Visibility Service")

@app.get("/")
def root():
    return {"message": "Sky Visibility Service is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
