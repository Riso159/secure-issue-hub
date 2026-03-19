from fastapi import FastAPI
from app.api.issues import router as issues_router
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.workspaces import router as workspaces_router
from app.api.members import router as members_router
from app.api.audit import router as audit_router
from app.api.comments import router as comments_router

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(members_router)
app.include_router(issues_router)
app.include_router(audit_router)
app.include_router(comments_router)

@app.get("/")
def read_root():
    return {"message": "API is running"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
