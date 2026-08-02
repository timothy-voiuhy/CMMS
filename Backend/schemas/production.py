from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.production import (
    ShiftType, ProductionLineStatus, ProductionOrderStatus
)


# Production Line Equipment Station Schemas
class ProductionLineEquipmentBase(BaseModel):
    equipment_id: int
    sequence_order: int
    station_name: Optional[str] = None
    operators: Optional[List[int]] = None
    cycle_time_minutes: Optional[float] = None
    notes: Optional[str] = None


class ProductionLineEquipmentCreate(ProductionLineEquipmentBase):
    production_line_id: int


class ProductionLineEquipmentUpdate(BaseModel):
    sequence_order: Optional[int] = None
    station_name: Optional[str] = None
    operators: Optional[List[int]] = None
    cycle_time_minutes: Optional[float] = None
    notes: Optional[str] = None


class ProductionLineEquipmentResponse(ProductionLineEquipmentBase):
    id: int
    production_line_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Production Line Schemas
class ProductionLineBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    capacity_per_hour: Optional[float] = None
    capacity_unit: Optional[str] = None
    location: Optional[str] = None
    floor: Optional[str] = None


class ProductionLineCreate(ProductionLineBase):
    line_code: str = Field(..., max_length=50)


class ProductionLineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProductionLineStatus] = None
    capacity_per_hour: Optional[float] = None
    capacity_unit: Optional[str] = None
    location: Optional[str] = None
    floor: Optional[str] = None


class ProductionLineResponse(ProductionLineBase):
    id: int
    line_code: str
    status: ProductionLineStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Shift Schemas
class ShiftBase(BaseModel):
    shift_type: ShiftType
    start_time: str = Field(..., max_length=10)
    end_time: str = Field(..., max_length=10)
    team_leader_id: Optional[int] = None
    operators: Optional[List[int]] = None
    active_days: Optional[List[int]] = None
    is_active: bool = True


class ShiftCreate(ShiftBase):
    production_line_id: int


class ShiftUpdate(BaseModel):
    shift_type: Optional[ShiftType] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    team_leader_id: Optional[int] = None
    operators: Optional[List[int]] = None
    active_days: Optional[List[int]] = None
    is_active: Optional[bool] = None


class ShiftResponse(ShiftBase):
    id: int
    production_line_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Production Order Schemas
class ProductionOrderBase(BaseModel):
    product_name: str = Field(..., max_length=200)
    product_code: Optional[str] = None
    target_quantity: float
    unit: str = Field(..., max_length=50)
    priority: int = Field(default=3, ge=1, le=5)
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    notes: Optional[str] = None


class ProductionOrderCreate(ProductionOrderBase):
    production_line_id: int
    shift_id: Optional[int] = None


class ProductionOrderUpdate(BaseModel):
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    target_quantity: Optional[float] = None
    produced_quantity: Optional[float] = None
    defect_quantity: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[ProductionOrderStatus] = None
    priority: Optional[int] = None
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    shift_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None


class ProductionOrderResponse(ProductionOrderBase):
    id: int
    order_number: str
    production_line_id: int
    produced_quantity: float
    defect_quantity: Optional[float] = None
    status: ProductionOrderStatus
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    shift_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    completion_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Packaging Order Schemas
class PackagingOrderBase(BaseModel):
    product_name: str = Field(..., max_length=200)
    product_code: Optional[str] = None
    target_quantity: float
    unit: str = Field(..., max_length=50)
    packaging_type: Optional[str] = None
    packaging_material: Optional[str] = None
    units_per_package: Optional[float] = None
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    notes: Optional[str] = None


class PackagingOrderCreate(PackagingOrderBase):
    production_order_id: Optional[int] = None
    assigned_to: Optional[int] = None


class PackagingOrderUpdate(BaseModel):
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    target_quantity: Optional[float] = None
    packaged_quantity: Optional[float] = None
    unit: Optional[str] = None
    packaging_type: Optional[str] = None
    packaging_material: Optional[str] = None
    units_per_package: Optional[float] = None
    status: Optional[ProductionOrderStatus] = None
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class PackagingOrderResponse(PackagingOrderBase):
    id: int
    order_number: str
    production_order_id: Optional[int] = None
    packaged_quantity: float
    status: ProductionOrderStatus
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
