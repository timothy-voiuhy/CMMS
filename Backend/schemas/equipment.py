from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.equipment import EquipmentStatus


class EquipmentBase(BaseModel):
    name: str = Field(..., max_length=200)
    equipment_id: str = Field(..., max_length=100)
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    status: EquipmentStatus = EquipmentStatus.OPERATIONAL
    purchase_date: Optional[str] = None
    warranty_expiry: Optional[str] = None
    specifications: Optional[str] = None
    notes: Optional[str] = None
    parent_id: Optional[int] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    specifications: Optional[str] = None
    notes: Optional[str] = None
    parent_id: Optional[int] = None


class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
