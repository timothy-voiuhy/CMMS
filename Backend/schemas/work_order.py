from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.work_order import WorkOrderType, WorkOrderPriority, WorkOrderStatus


class WorkOrderBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    work_order_type: WorkOrderType
    priority: WorkOrderPriority = WorkOrderPriority.MEDIUM
    equipment_id: Optional[int] = None
    scheduled_date: Optional[str] = None
    due_date: Optional[str] = None
    estimated_hours: Optional[float] = None
    notes: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[WorkOrderPriority] = None
    status: Optional[WorkOrderStatus] = None
    assigned_to: Optional[int] = None
    scheduled_date: Optional[str] = None
    due_date: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None


class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus
    notes: Optional[str] = None


class WorkOrderAssign(BaseModel):
    craftsman_id: int


class WorkOrderResponse(WorkOrderBase):
    id: int
    work_order_number: str
    status: WorkOrderStatus
    assigned_to: Optional[int] = None
    created_by: int
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    actual_hours: Optional[float] = None
    completion_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
