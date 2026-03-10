from datetime import datetime, timezone
import uuid

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import ROLE_OWNER
from app.db.database import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.services.sessions import get_session


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    sid = request.cookies.get(settings.session_cookie_name)
    if not sid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        sid_uuid = uuid.UUID(sid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        )

    sess = get_session(db, sid_uuid)
    if not sess or sess.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    if sess.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        )

    user = db.get(User, sess.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    return user


def csrf_protect(request: Request) -> None:
    csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="CSRF check failed"
        )


def require_workspace_member(
    workspace_id: int, user_id: int, db: Session
) -> WorkspaceMember:
    stmt = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    )
    member = db.execute(stmt).scalars().first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member"
        )
    return member


def require_workspace_owner(
    workspace_id: int, user_id: int, db: Session
) -> WorkspaceMember:
    member = require_workspace_member(workspace_id, user_id, db)
    if member.role != ROLE_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required"
        )
    return member
