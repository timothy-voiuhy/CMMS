from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.quality import InspectionStatus, InspectionResult, NCRStatus, NCRSeverity


# ==================== INSPECTION ITEM SCHEMAS ====================

class QualityInspectionItemBase(BaseModel):
    checkpoint_name: str
    specification: Optional[str] = None
    measured_value: Optional[str] = None
    result: InspectionResult = InspectionResult.PENDING
    notes: Optional[str] = None


class QualityInspectionItemCreate(QualityInspectionItemBase):
    pass


class QualityInspectionItemResponse(QualityInspectionItemBase):
    id: int
    inspection_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== QUALITY INSPECTION SCHEMAS ====================

class QualityInspectionBase(BaseModel):
    production_order_id: Optional[int] = None
    batch_number: Optional[str] = None
    product_name: str
    inspection_type: str
    inspection_date: datetime
    sample_size: Optional[int] = None
    specifications: Optional[str] = None
    observations: Optional[str] = None
    notes: Optional[str] = None


class QualityInspectionCreate(QualityInspectionBase):
    inspector_id: int
    inspection_items: List[QualityInspectionItemCreate] = []


class QualityInspectionUpdate(BaseModel):
    production_order_id: Optional[int] = None
    batch_number: Optional[str] = None
    product_name: Optional[str] = None
    inspection_type: Optional[str] = None
    inspection_date: Optional[datetime] = None
    sample_size: Optional[int] = None
    defects_found: Optional[int] = None
    specifications: Optional[str] = None
    status: Optional[InspectionStatus] = None
    result: Optional[InspectionResult] = None
    pass_rate: Optional[float] = None
    observations: Optional[str] = None
    notes: Optional[str] = None


class QualityInspectionResponse(QualityInspectionBase):
    id: int
    inspection_number: str
    inspector_id: int
    defects_found: int
    status: InspectionStatus
    result: InspectionResult
    pass_rate: Optional[float]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    inspection_items: List[QualityInspectionItemResponse] = []

    class Config:
        from_attributes = True


# ==================== NCR SCHEMAS ====================

class NonConformanceReportBase(BaseModel):
    inspection_id: Optional[int] = None
    production_order_id: Optional[int] = None
    equipment_id: Optional[int] = None
    batch_number: Optional[str] = None
    title: str
    description: str
    severity: NCRSeverity = NCRSeverity.MINOR
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    estimated_cost: Optional[float] = None


class NonConformanceReportCreate(NonConformanceReportBase):
    reported_by_id: int
    assigned_to_id: Optional[int] = None


class NonConformanceReportUpdate(BaseModel):
    inspection_id: Optional[int] = None
    production_order_id: Optional[int] = None
    equipment_id: Optional[int] = None
    batch_number: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[NCRSeverity] = None
    status: Optional[NCRStatus] = None
    assigned_to_id: Optional[int] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    estimated_cost: Optional[float] = None


class NonConformanceReportResponse(NonConformanceReportBase):
    id: int
    ncr_number: str
    status: NCRStatus
    reported_by_id: int
    assigned_to_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== STATISTICS SCHEMAS ====================

class QualityStatistics(BaseModel):
    total_inspections: int
    pending_inspections: int
    completed_inspections: int
    pass_rate: float
    fail_rate: float
    total_ncrs: int
    open_ncrs: int
    critical_ncrs: int
    avg_defects_per_inspection: float
