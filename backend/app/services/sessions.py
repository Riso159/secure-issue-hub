from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.session import UserSession


def create_session(db: Session, user_id: int) -> UserSession:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.session_expire_minutes)

    sess = UserSession(
        user_id=user_id,
        csrf_token=token_urlsafe(32),
        expires_at=expires,
        revoked_at=None,
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess


def get_session(db: Session, session_id) -> UserSession | None:
    stmt = select(UserSession).where(UserSession.id == session_id)
    return db.execute(stmt).scalars().first()


def revoke_session(db: Session, sess: UserSession) -> None:
    sess.revoked_at = datetime.now(timezone.utc)
    db.add(sess)
    db.commit()
