from datetime import datetime, timezone
import uuid

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.services.sessions import get_session


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    sid = request.cookies.get(settings.session_cookie_name)
    if not sid:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        sid_uuid = uuid.UUID(sid)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid session")

    sess = get_session(db, sid_uuid)
    if not sess or sess.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if sess.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    user = db.get(User, sess.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user


def csrf_protect(request: Request) -> None:
    csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="CSRF check failed"
        )
