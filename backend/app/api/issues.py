from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.deps import (
    csrf_protect,
    get_current_user,
    require_workspace_member,
    require_workspace_owner,
)
from app.core.roles import ROLE_OWNER, ROLE_SECURITY_REVIEWER
from app.db.database import get_db
from app.models.user import User
from app.schemas.issues import IssueCreate, IssueOut, IssueUpdate
from app.services.audit import log_event
from app.services.issues import (
    create_issue,
    get_issue,
    list_issues,
    soft_delete_issue,
    update_issue,
)

router = APIRouter(tags=["issues"])


@router.get("/workspaces/{workspace_id}/issues", response_model=list[IssueOut])
def list_for_workspace(
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_workspace_member(workspace_id, user.id, db)
    items = list_issues(db, workspace_id)

    return [
        IssueOut(
            id=i.id,
            workspace_id=i.workspace_id,
            title=i.title,
            description=i.description,
            severity=i.severity.value,
            status=i.status.value,
            created_by_id=i.created_by_id,
            assignee_id=i.assignee_id,
        )
        for i in items
    ]


@router.post("/workspaces/{workspace_id}/issues", response_model=IssueOut)
def create_in_workspace(
    workspace_id: int,
    payload: IssueCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf: None = Depends(csrf_protect),
):
    require_workspace_member(workspace_id, user.id, db)

    issue = create_issue(
        db,
        workspace_id,
        user.id,
        payload.title,
        payload.description,
        payload.severity,
    )

    log_event(
        db,
        request,
        action="ISSUE_CREATED",
        target_type="issue",
        target_id=str(issue.id),
        workspace_id=workspace_id,
        actor_id=user.id,
        metadata={
            "title": issue.title,
            "severity": issue.severity.value,
        },
    )

    return IssueOut(
        id=issue.id,
        workspace_id=issue.workspace_id,
        title=issue.title,
        description=issue.description,
        severity=issue.severity.value,
        status=issue.status.value,
        created_by_id=issue.created_by_id,
        assignee_id=issue.assignee_id,
    )


@router.patch("/issues/{issue_id}", response_model=IssueOut)
def patch_issue(
    issue_id: int,
    payload: IssueUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf: None = Depends(csrf_protect),
):
    issue = get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    member = require_workspace_member(issue.workspace_id, user.id, db)
    data = payload.model_dump(exclude_unset=True)

    if "assignee_id" in data and member.role != ROLE_OWNER:
        raise HTTPException(
            status_code=403,
            detail="Owner role required to set assignee",
        )

    if "severity" in data and member.role not in {
        ROLE_OWNER,
        ROLE_SECURITY_REVIEWER,
    }:
        raise HTTPException(
            status_code=403,
            detail="Owner or Security Reviewer required to change severity",
        )

    issue = update_issue(db, issue, data)

    return IssueOut(
        id=issue.id,
        workspace_id=issue.workspace_id,
        title=issue.title,
        description=issue.description,
        severity=issue.severity.value,
        status=issue.status.value,
        created_by_id=issue.created_by_id,
        assignee_id=issue.assignee_id,
    )


@router.delete("/issues/{issue_id}")
def delete_issue(
    issue_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf: None = Depends(csrf_protect),
):
    issue = get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    require_workspace_owner(issue.workspace_id, user.id, db)
    soft_delete_issue(db, issue)

    return {"ok": True}
