from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.inventory import RequisitionStatus, RequisitionLineStatus, RequisitionPriority


# ==================== CATEGORY SCHEMAS ====================

class InventoryCategoryBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class InventoryCategoryCreate(InventoryCategoryBase):
    pass


class InventoryCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class InventoryCategoryResponse(InventoryCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryCategoryTree(InventoryCategoryResponse):
    """Category with children for tree view"""
    children: List['InventoryCategoryTree'] = []
    
    class Config:
        from_attributes = True


# ==================== ITEM SCHEMAS ====================

class InventoryItemBase(BaseModel):
    item_code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: int
    unit_of_measure: str = Field(..., max_length=20)
    quantity: float = 0.0
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None
    reorder_point: Optional[float] = None
    unit_cost: Optional[float] = None
    location: Optional[str] = None
    supplier: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    notes: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_of_measure: Optional[str] = None
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None
    reorder_point: Optional[float] = None
    unit_cost: Optional[float] = None
    location: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryItemWithCategory(InventoryItemResponse):
    """Item with full category details"""
    category: Optional[InventoryCategoryResponse] = None
    
    class Config:
        from_attributes = True


# ==================== TRANSACTION SCHEMAS ====================

class InventoryTransactionBase(BaseModel):
    item_id: int
    transaction_type: str  # TransactionType enum as string
    quantity: float
    unit_cost: Optional[float] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class InventoryTransactionCreate(InventoryTransactionBase):
    performed_by: Optional[int] = None


class InventoryTransactionResponse(InventoryTransactionBase):
    id: int
    performed_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== REQUISITION SCHEMAS ====================

class InventoryItemSummary(BaseModel):
    id: int
    item_code: str
    name: str
    unit_of_measure: str
    quantity: float
    location: Optional[str] = None

    class Config:
        from_attributes = True


class InventoryRequisitionItemCreate(BaseModel):
    item_id: int
    requested_quantity: float = Field(..., gt=0)
    notes: Optional[str] = None


class InventoryRequisitionItemUpdate(BaseModel):
    item_id: Optional[int] = None
    requested_quantity: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None


class InventoryRequisitionItemResponse(BaseModel):
    id: int
    requisition_id: int
    item_id: int
    requested_quantity: float
    approved_quantity: Optional[float] = None
    fulfilled_quantity: float
    unit_of_measure: str
    notes: Optional[str] = None
    status: RequisitionLineStatus
    item: Optional[InventoryItemSummary] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryRequisitionBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    priority: RequisitionPriority = RequisitionPriority.MEDIUM
    needed_by: Optional[str] = None
    department: Optional[str] = Field(None, max_length=100)
    work_order_id: Optional[int] = None
    production_order_id: Optional[int] = None
    notes: Optional[str] = None


class InventoryRequisitionCreate(InventoryRequisitionBase):
    items: List[InventoryRequisitionItemCreate] = Field(..., min_length=1)


class InventoryRequisitionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[RequisitionPriority] = None
    needed_by: Optional[str] = None
    department: Optional[str] = Field(None, max_length=100)
    work_order_id: Optional[int] = None
    production_order_id: Optional[int] = None
    notes: Optional[str] = None
    items: Optional[List[InventoryRequisitionItemCreate]] = None


class InventoryRequisitionListResponse(InventoryRequisitionBase):
    id: int
    requisition_number: str
    status: RequisitionStatus
    requested_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    fulfilled_by: Optional[int] = None
    fulfilled_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    line_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryRequisitionResponse(InventoryRequisitionListResponse):
    items: List[InventoryRequisitionItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class InventoryRequisitionApprovalLine(BaseModel):
    line_id: int
    approved_quantity: float = Field(..., ge=0)


class InventoryRequisitionApprovalRequest(BaseModel):
    items: Optional[List[InventoryRequisitionApprovalLine]] = None
    notes: Optional[str] = None


class InventoryRequisitionRejectRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class InventoryRequisitionFulfillmentLine(BaseModel):
    line_id: int
    quantity: float = Field(..., gt=0)


class InventoryRequisitionFulfillmentRequest(BaseModel):
    items: List[InventoryRequisitionFulfillmentLine] = Field(..., min_length=1)
    notes: Optional[str] = None
