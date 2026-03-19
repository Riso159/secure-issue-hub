from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import csrf_protect, get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.workspaces import WorkspaceCreate, WorkspaceOut
from app.services.audit import log_event
from app.services.workspaces import create_workspace, list_workspaces_for_user

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceOut])
def list_my_workspaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = list_workspaces_for_user(db, user.id)
    return [
        WorkspaceOut(
            id=w.id,
            name=w.name,
            owner_id=w.owner_id,
        )
        for w in items
    ]


@router.post("", response_model=WorkspaceOut)
def create(
    payload: WorkspaceCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf: None = Depends(csrf_protect),
):
    ws = create_workspace(db, user.id, payload.name)

    log_event(
        db,
        request,
        action="WORKSPACE_CREATED",
        target_type="workspace",
        target_id=str(ws.id),
        workspace_id=ws.id,
        actor_id=user.id,
        metadata={"name": ws.name},
    )

    return WorkspaceOut(
        id=ws.id,
        name=ws.name,
        owner_id=ws.owner_id,
    )
