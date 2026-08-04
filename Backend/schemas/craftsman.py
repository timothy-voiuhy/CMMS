from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SkillBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CraftsmanBase(BaseModel):
    employee_id: str = Field(..., max_length=50)
    department: Optional[str] = None
    position: Optional[str] = None
    role_id: Optional[int] = None
    hire_date: Optional[str] = None
    certification_level: Optional[str] = None
    hourly_rate: Optional[float] = None
    notes: Optional[str] = None


class CraftsmanCreate(CraftsmanBase):
    user_id: int


class CraftsmanUpdate(BaseModel):
    department: Optional[str] = None
    position: Optional[str] = None
    role_id: Optional[int] = None
    certification_level: Optional[str] = None
    hourly_rate: Optional[float] = None
    notes: Optional[str] = None


class CraftsmanResponse(CraftsmanBase):
    id: int
    user_id: int
    role_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    skills: List[SkillResponse] = []
    
    class Config:
        from_attributes = True


class CraftsmanWithUser(CraftsmanResponse):
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role_name: Optional[str] = None  # Role name for display
