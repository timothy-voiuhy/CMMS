from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    level: int = 1
    category: Optional[str] = None
    permissions_json: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    category: Optional[str] = None
    permissions_json: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    is_system_role: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
