import json
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_event(
    db: Session,
    request: Request,
    action: str,
    target_type: str,
    target_id: str | None = None,
    workspace_id: int | None = None,
    actor_id: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    ip: str | None = None
    if request.client is not None:
        ip = request.client.host

    user_agent = request.headers.get("user-agent")

    entry = AuditLog(
        workspace_id=workspace_id,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip_address=ip,
        user_agent=user_agent,
        metadata_json=json.dumps(metadata) if metadata is not None else None,
    )

    db.add(entry)
    db.commit()
