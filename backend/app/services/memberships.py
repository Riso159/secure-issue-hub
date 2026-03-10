from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.workspace_member import WorkspaceMember
from app.services.users import get_user_by_email
from app.core.roles import ALL_ROLES


def get_membership(
    db: Session, workspace_id: int, user_id: int
) -> WorkspaceMember | None:
    stmt = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    )
    return db.execute(stmt).scalars().first()


def list_members(db: Session, workspace_id: int) -> list[WorkspaceMember]:
    stmt = (
        select(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
        .order_by(WorkspaceMember.user_id)
    )
    return list(db.execute(stmt).scalars().all())


def add_member_by_email(
    db: Session, workspace_id: int, email: str, role: str
) -> WorkspaceMember:
    if role not in ALL_ROLES:
        raise ValueError("Invalid role")

    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("User not found")

    member = WorkspaceMember(workspace_id=workspace_id, user_id=user.id, role=role)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Member already exists")

    db.refresh(member)
    return member


def update_member_role(
    db: Session, workspace_id: int, user_id: int, role: str
) -> WorkspaceMember:
    if role not in ALL_ROLES:
        raise ValueError("Invalid role")

    member = get_membership(db, workspace_id, user_id)
    if not member:
        raise ValueError("Member not found")

    member.role = role
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_member(db: Session, workspace_id: int, user_id: int) -> None:
    member = get_membership(db, workspace_id, user_id)
    if not member:
        raise ValueError("Member not found")

    db.delete(member)
    db.commit()
