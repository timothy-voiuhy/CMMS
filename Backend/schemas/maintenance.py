from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.maintenance import MaintenanceCatalogueItemType


class MaintenanceReportBase(BaseModel):
    work_order_id: int
    equipment_id: int
    work_performed: str
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    parts_used: Optional[str] = None
    labor_hours: Optional[float] = None
    equipment_operational: bool = True
    follow_up_required: bool = False


class MaintenanceReportCreate(MaintenanceReportBase):
    craftsman_id: int


class MaintenanceReportUpdate(BaseModel):
    work_performed: Optional[str] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    parts_used: Optional[str] = None
    labor_hours: Optional[float] = None
    equipment_operational: Optional[bool] = None
    follow_up_required: Optional[bool] = None
    attachments: Optional[str] = None


class MaintenanceReportResponse(MaintenanceReportBase):
    id: int
    report_number: str
    craftsman_id: int
    attachments: Optional[str] = None
    completed_at: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MaintenanceReportWithDetails(MaintenanceReportResponse):
    """Extended response with related entity details."""
    equipment_name: Optional[str] = None
    craftsman_name: Optional[str] = None
    work_order_number: Optional[str] = None
    reviewer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class MaintenanceCatalogueItemBase(BaseModel):
    item_code: Optional[str] = Field(None, max_length=100)
    item_type: MaintenanceCatalogueItemType = MaintenanceCatalogueItemType.SPARE_PART
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    manufacturer: Optional[str] = Field(None, max_length=200)
    model_number: Optional[str] = Field(None, max_length=100)
    supplier: Optional[str] = Field(None, max_length=200)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    unit_cost: Optional[float] = None
    location: Optional[str] = Field(None, max_length=200)
    compatible_equipment: Optional[str] = None
    inventory_item_id: Optional[int] = None
    is_active: bool = True
    notes: Optional[str] = None


class MaintenanceCatalogueItemCreate(MaintenanceCatalogueItemBase):
    pass


class MaintenanceCatalogueItemUpdate(BaseModel):
    item_code: Optional[str] = Field(None, max_length=100)
    item_type: Optional[MaintenanceCatalogueItemType] = None
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    manufacturer: Optional[str] = Field(None, max_length=200)
    model_number: Optional[str] = Field(None, max_length=100)
    supplier: Optional[str] = Field(None, max_length=200)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    unit_cost: Optional[float] = None
    location: Optional[str] = Field(None, max_length=200)
    compatible_equipment: Optional[str] = None
    inventory_item_id: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class MaintenanceCatalogueItemResponse(MaintenanceCatalogueItemBase):
    id: int
    item_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
