from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/")
def read_root():
    return {"message": "API is running"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
