from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, field_validator


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    level: int = 1
    category: Optional[str] = None
    permissions_json: Optional[str] = None
    is_active: bool = True
    is_system_role: bool = False


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    category: Optional[str] = None
    permissions_json: Optional[str] = None
    is_active: Optional[bool] = None
    is_system_role: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    is_system_role: bool
    created_at: Union[datetime, str]
    updated_at: Union[datetime, str]

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v) if v is not None else ""

    class Config:
        from_attributes = True


# ==================== RBAC SCHEMAS ====================

class RolePermissionsUpdate(BaseModel):
    """Schema for updating role permissions."""
    permissions: List[str]
    template: Optional[str] = None
    custom: bool = False

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        """Validate permission format (must contain a dot separator)."""
        for perm in v:
            if not perm:
                raise ValueError("Empty permission string is not allowed")
            # Allow wildcards like "equipment.*" and special "*"
            if perm == "*":
                continue
            if "." not in perm and not perm.endswith(".*"):
                raise ValueError(f"Invalid permission format: {perm}. Must be 'resource.action'")
        return v


class RoleWithPermissions(RoleResponse):
    """Role response with parsed permissions list."""
    parsed_permissions: List[str] = []


class PermissionDefinition(BaseModel):
    """Individual permission definition."""
    key: str
    name: str
    description: str
    category: str
    implies: List[str] = []


class PermissionRegistry(BaseModel):
    """Complete permission registry response."""
    permissions: List[PermissionDefinition]
    categories: List[str]


class RoleTemplateInfo(BaseModel):
    """Role template information."""
    key: str
    name: str
    description: str
    level: int
    category: str
    permissions: List[str]


class CreateRoleFromTemplate(BaseModel):
    """Schema for creating a role from a template."""
    name: str
    template: str
    description: Optional[str] = None
    level: Optional[int] = None
    category: Optional[str] = None
