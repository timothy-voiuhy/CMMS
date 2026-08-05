from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models.sales import SalesOrderStatus, SalesOrderLineStatus, SalesOrderPriority


# ==================== CUSTOMER SCHEMAS ====================

class CustomerBase(BaseModel):
    customer_code: Optional[str] = Field(None, max_length=100)
    name: str = Field(..., max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    payment_terms: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[float] = None
    is_active: bool = True
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_code: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    payment_terms: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    customer_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    id: int
    customer_code: str
    name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== SALES ORDER SCHEMAS ====================

class InventoryItemSalesSummary(BaseModel):
    id: int
    item_code: str
    name: str
    unit_of_measure: str
    quantity: float
    unit_cost: Optional[float] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True


class SalesOrderItemCreate(BaseModel):
    item_id: int
    ordered_quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    tax_rate: float = Field(0.0, ge=0)
    discount_amount: float = Field(0.0, ge=0)
    notes: Optional[str] = None


class SalesOrderItemResponse(BaseModel):
    id: int
    sales_order_id: int
    item_id: int
    item_code: str
    item_name: str
    ordered_quantity: float
    fulfilled_quantity: float
    unit_of_measure: str
    unit_price: float
    tax_rate: float
    discount_amount: float
    line_total: float
    notes: Optional[str] = None
    status: SalesOrderLineStatus
    item: Optional[InventoryItemSalesSummary] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalesOrderBase(BaseModel):
    customer_id: int
    priority: SalesOrderPriority = SalesOrderPriority.MEDIUM
    order_date: Optional[str] = None
    requested_delivery_date: Optional[str] = None
    currency: str = Field("USD", max_length=10)
    notes: Optional[str] = None


class SalesOrderCreate(SalesOrderBase):
    items: List[SalesOrderItemCreate] = Field(..., min_length=1)


class SalesOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    priority: Optional[SalesOrderPriority] = None
    order_date: Optional[str] = None
    requested_delivery_date: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None
    items: Optional[List[SalesOrderItemCreate]] = None


class SalesOrderListResponse(SalesOrderBase):
    id: int
    order_number: str
    status: SalesOrderStatus
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    created_by: int
    confirmed_by: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    fulfilled_by: Optional[int] = None
    fulfilled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    line_count: int = 0
    customer: Optional[CustomerSummary] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalesOrderResponse(SalesOrderListResponse):
    items: List[SalesOrderItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SalesOrderFulfillmentLine(BaseModel):
    line_id: int
    quantity: float = Field(..., gt=0)


class SalesOrderFulfillmentRequest(BaseModel):
    items: List[SalesOrderFulfillmentLine] = Field(..., min_length=1)
    notes: Optional[str] = None


class SalesOrderCancelRequest(BaseModel):
    reason: str = Field(..., min_length=1)
