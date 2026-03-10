from fastapi import FastAPI

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.workspaces import router as workspaces_router

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(workspaces_router)


@app.get("/")
def read_root():
    return {"message": "API is running"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
