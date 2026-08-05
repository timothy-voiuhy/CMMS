from sqlalchemy import Column, Integer, String, Float, Text, Enum as SQLEnum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel
import enum


class SalesOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class SalesOrderLineStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class SalesOrderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Customer(Base, BaseModel):
    __tablename__ = "customers"

    customer_code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    tax_id = Column(String(100), nullable=True)
    payment_terms = Column(String(100), nullable=True)
    credit_limit = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    orders = relationship("SalesOrder", back_populates="customer")


class SalesOrder(Base, BaseModel):
    __tablename__ = "sales_orders"

    order_number = Column(String(100), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    status = Column(SQLEnum(SalesOrderStatus), default=SalesOrderStatus.DRAFT, nullable=False, index=True)
    priority = Column(SQLEnum(SalesOrderPriority), default=SalesOrderPriority.MEDIUM, nullable=False)

    order_date = Column(String(20), nullable=True)
    requested_delivery_date = Column(String(20), nullable=True)
    currency = Column(String(10), default="USD", nullable=False)

    subtotal = Column(Float, default=0.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    fulfilled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="orders")
    items = relationship(
        "SalesOrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="SalesOrderItem.id",
    )
    creator = relationship("User", foreign_keys=[created_by])
    confirmer = relationship("User", foreign_keys=[confirmed_by])
    fulfiller = relationship("User", foreign_keys=[fulfilled_by])
    canceller = relationship("User", foreign_keys=[cancelled_by])

    @property
    def line_count(self) -> int:
        return len(self.items or [])


class SalesOrderItem(Base, BaseModel):
    __tablename__ = "sales_order_items"

    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    item_code = Column(String(100), nullable=False)
    item_name = Column(String(200), nullable=False)
    ordered_quantity = Column(Float, nullable=False)
    fulfilled_quantity = Column(Float, default=0.0, nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    line_total = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(SQLEnum(SalesOrderLineStatus), default=SalesOrderLineStatus.PENDING, nullable=False)

    order = relationship("SalesOrder", back_populates="items")
    item = relationship("InventoryItem")
