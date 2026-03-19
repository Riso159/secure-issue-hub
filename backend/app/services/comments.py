from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment


def create_comment(
    db: Session,
    issue_id: int,
    author_id: int,
    content: str,
) -> Comment:
    comment = Comment(
        issue_id=issue_id,
        author_id=author_id,
        content=content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, issue_id: int) -> list[Comment]:
    stmt = (
        select(Comment)
        .where(Comment.issue_id == issue_id)
        .order_by(Comment.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def update_comment_content(db: Session, comment: Comment, content: str) -> Comment:
    comment.content = content
    comment.updated_at = datetime.now(timezone.utc)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment