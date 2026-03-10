from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember


ROLE_OWNER = "OWNER"


def create_workspace(db: Session, owner_id: int, name: str) -> Workspace:
    ws = Workspace(name=name, owner_id=owner_id)
    db.add(ws)
    db.flush()  # aby ws.id bolo dostupné ešte pred commitom

    member = WorkspaceMember(workspace_id=ws.id, user_id=owner_id, role=ROLE_OWNER)
    db.add(member)

    db.commit()
    db.refresh(ws)
    return ws


def list_workspaces_for_user(db: Session, user_id: int) -> list[Workspace]:
    stmt = (
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user_id)
        .order_by(Workspace.id.desc())
    )
    return list(db.execute(stmt).scalars().all())
