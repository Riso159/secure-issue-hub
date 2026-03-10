from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, csrf_protect
from app.db.database import get_db
from app.schemas.workspaces import WorkspaceCreate, WorkspaceOut
from app.services.workspaces import create_workspace, list_workspaces_for_user


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceOut])
def list_my_workspaces(user=Depends(get_current_user), db: Session = Depends(get_db)):
    items = list_workspaces_for_user(db, user.id)
    return [WorkspaceOut(id=w.id, name=w.name, owner_id=w.owner_id) for w in items]


@router.post("", response_model=WorkspaceOut)
def create(
    payload: WorkspaceCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    ws = create_workspace(db, user.id, payload.name)
    return WorkspaceOut(id=ws.id, name=ws.name, owner_id=ws.owner_id)
