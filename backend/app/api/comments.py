from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.deps import csrf_protect, get_current_user, require_workspace_member
from app.db.database import get_db
from app.models.user import User
from app.schemas.comments import CommentCreate, CommentOut
from app.services.audit import log_event
from app.services.comments import create_comment, list_comments
from app.services.issues import get_issue

router = APIRouter(tags=["comments"])


@router.get("/issues/{issue_id}/comments", response_model=list[CommentOut])
def get_issue_comments(
    issue_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    issue = get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    require_workspace_member(issue.workspace_id, user.id, db)
    items = list_comments(db, issue_id)

    return [
        CommentOut(
            id=c.id,
            issue_id=c.issue_id,
            author_id=c.author_id,
            content=c.content,
            created_at=c.created_at.isoformat(),
        )
        for c in items
    ]


@router.post("/issues/{issue_id}/comments", response_model=CommentOut)
def create_issue_comment(
    issue_id: int,
    payload: CommentCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf: None = Depends(csrf_protect),
):
    issue = get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    require_workspace_member(issue.workspace_id, user.id, db)

    comment = create_comment(
        db=db,
        issue_id=issue_id,
        author_id=user.id,
        content=payload.content,
    )

    log_event(
        db,
        request,
        action="COMMENT_CREATED",
        target_type="comment",
        target_id=str(comment.id),
        workspace_id=issue.workspace_id,
        actor_id=user.id,
        metadata={"issue_id": issue_id},
    )

    return CommentOut(
        id=comment.id,
        issue_id=comment.issue_id,
        author_id=comment.author_id,
        content=comment.content,
        created_at=comment.created_at.isoformat(),
    )