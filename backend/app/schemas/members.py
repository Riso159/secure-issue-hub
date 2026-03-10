from pydantic import BaseModel, EmailStr
from typing import Literal

Role = Literal["OWNER", "DEVELOPER", "SECURITY_REVIEWER"]


class AddMemberRequest(BaseModel):
    email: EmailStr
    role: Role = "DEVELOPER"


class UpdateRoleRequest(BaseModel):
    role: Role


class MemberOut(BaseModel):
    user_id: int
    role: Role
