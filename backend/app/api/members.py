from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_user,
    csrf_protect,
    require_workspace_owner,
    require_workspace_member,
)
from app.db.database import get_db
from app.schemas.members import AddMemberRequest, UpdateRoleRequest, MemberOut
from app.services.memberships import (
    add_member_by_email,
    list_members,
    update_member_role,
    remove_member,
)


router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["members"])


@router.get("", response_model=list[MemberOut])
def members_list(
    workspace_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    # stačí byť člen
    require_workspace_member(workspace_id, user.id, db)
    items = list_members(db, workspace_id)
    return [MemberOut(user_id=m.user_id, role=m.role) for m in items]


@router.post("", response_model=MemberOut)
def add_member(
    workspace_id: int,
    payload: AddMemberRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    # iba OWNER môže pridávať
    require_workspace_owner(workspace_id, user.id, db)
    try:
        m = add_member_by_email(db, workspace_id, payload.email, payload.role)
        return MemberOut(user_id=m.user_id, role=m.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{member_user_id}", response_model=MemberOut)
def change_role(
    workspace_id: int,
    member_user_id: int,
    payload: UpdateRoleRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    require_workspace_owner(workspace_id, user.id, db)
    try:
        m = update_member_role(db, workspace_id, member_user_id, payload.role)
        return MemberOut(user_id=m.user_id, role=m.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{member_user_id}")
def delete_member(
    workspace_id: int,
    member_user_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    require_workspace_owner(workspace_id, user.id, db)
    try:
        remove_member(db, workspace_id, member_user_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
