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


class SalesInvoiceStatus(str, enum.Enum):
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    VOIDED = "voided"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    CHEQUE = "cheque"
    OTHER = "other"


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
    invoice = relationship("SalesInvoice", back_populates="sales_order", uselist=False)

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


class SalesInvoice(Base, BaseModel):
    __tablename__ = "sales_invoices"

    invoice_number = Column(String(100), unique=True, index=True, nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    status = Column(SQLEnum(SalesInvoiceStatus), default=SalesInvoiceStatus.ISSUED, nullable=False, index=True)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    currency = Column(String(10), nullable=False)
    subtotal = Column(Float, default=0.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    amount_paid = Column(Float, default=0.0, nullable=False)
    balance_due = Column(Float, default=0.0, nullable=False)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    issued_at = Column(DateTime, nullable=False)
    voided_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    voided_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    sales_order = relationship("SalesOrder", back_populates="invoice")
    customer = relationship("Customer")
    items = relationship("SalesInvoiceItem", back_populates="invoice", cascade="all, delete-orphan", order_by="SalesInvoiceItem.id")
    receipts = relationship("SalesReceipt", back_populates="invoice", cascade="all, delete-orphan", order_by="SalesReceipt.id")
    issuer = relationship("User", foreign_keys=[issued_by])
    voider = relationship("User", foreign_keys=[voided_by])


class SalesInvoiceItem(Base, BaseModel):
    __tablename__ = "sales_invoice_items"

    invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=False, index=True)
    sales_order_item_id = Column(Integer, ForeignKey("sales_order_items.id"), nullable=True)
    item_code = Column(String(100), nullable=False)
    item_name = Column(String(200), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    line_total = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)

    invoice = relationship("SalesInvoice", back_populates="items")
    sales_order_item = relationship("SalesOrderItem")


class SalesReceipt(Base, BaseModel):
    __tablename__ = "sales_receipts"

    receipt_number = Column(String(100), unique=True, index=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=False, index=True)
    receipt_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    reference = Column(String(200), nullable=True)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)

    invoice = relationship("SalesInvoice", back_populates="receipts")
    receiver = relationship("User", foreign_keys=[received_by])
