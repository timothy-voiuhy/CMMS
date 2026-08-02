from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


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
