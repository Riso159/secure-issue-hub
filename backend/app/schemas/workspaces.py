from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class WorkspaceOut(BaseModel):
    id: int
    name: str
    owner_id: int
