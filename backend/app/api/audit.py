from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_workspace_member
from app.db.database import get_db
from app.models.audit_log import AuditLog


router = APIRouter(prefix="/workspaces/{workspace_id}/audit", tags=["audit"])


@router.get("")
def list_audit(
    workspace_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    require_workspace_member(workspace_id, user.id, db)
    stmt = (
        select(AuditLog)
        .where(AuditLog.workspace_id == workspace_id)
        .order_by(AuditLog.id.desc())
        .limit(200)
    )
    rows = db.execute(stmt).scalars().all()
    return [
        {
            "id": r.id,
            "action": r.action,
            "target_type": r.target_type,
            "target_id": r.target_id,
            "actor_id": r.actor_id,
            "ip_address": r.ip_address,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
