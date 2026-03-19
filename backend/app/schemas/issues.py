from pydantic import BaseModel, Field
from typing import Literal


Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
Status = Literal["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]


class IssueCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=10000)
    severity: Severity = "MEDIUM"


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    severity: Severity | None = None
    status: Status | None = None
    assignee_id: int | None = None


class IssueOut(BaseModel):
    id: int
    workspace_id: int
    title: str
    description: str
    severity: Severity
    status: Status
    created_by_id: int
    assignee_id: int | None
