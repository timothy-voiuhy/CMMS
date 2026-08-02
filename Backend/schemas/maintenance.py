from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


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
