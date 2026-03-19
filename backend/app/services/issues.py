from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.issue import Issue, IssueSeverity, IssueStatus


def create_issue(
    db: Session,
    workspace_id: int,
    created_by_id: int,
    title: str,
    description: str,
    severity: str,
) -> Issue:
    issue = Issue(
        workspace_id=workspace_id,
        created_by_id=created_by_id,
        title=title,
        description=description,
        severity=IssueSeverity(severity),
        status=IssueStatus.OPEN,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def list_issues(db: Session, workspace_id: int) -> list[Issue]:
    stmt = (
        select(Issue)
        .where(Issue.workspace_id == workspace_id, Issue.deleted_at.is_(None))
        .order_by(Issue.id.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_issue(db: Session, issue_id: int) -> Issue | None:
    issue = db.get(Issue, issue_id)
    if not issue or issue.deleted_at is not None:
        return None
    return issue


def update_issue(db: Session, issue: Issue, data: dict) -> Issue:
    # data je už "exclude_unset" z Pydantic
    if "title" in data:
        issue.title = data["title"]
    if "description" in data:
        issue.description = data["description"]
    if "severity" in data:
        issue.severity = IssueSeverity(data["severity"])
    if "status" in data:
        issue.status = IssueStatus(data["status"])
    if "assignee_id" in data:
        issue.assignee_id = data["assignee_id"]

    issue.updated_at = datetime.now(timezone.utc)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def soft_delete_issue(db: Session, issue: Issue) -> None:
    issue.deleted_at = datetime.now(timezone.utc)
    db.add(issue)
    db.commit()
