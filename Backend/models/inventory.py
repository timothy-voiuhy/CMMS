from sqlalchemy import Column, Integer, String, Float, Text, Enum as SQLEnum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel
import enum


class InventoryCategory(Base, BaseModel):
    """Hierarchical inventory categories (e.g., Flavors -> BBQ Flavor, Salt & Vinegar)"""
    __tablename__ = "inventory_categories"
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("inventory_categories.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Self-referential relationships
    parent = relationship("InventoryCategory", remote_side="InventoryCategory.id", backref="children")
    
    # Relationship to inventory items
    items = relationship("InventoryItem", back_populates="category")


class InventoryItem(Base, BaseModel):
    __tablename__ = "inventory_items"
    
    item_code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("inventory_categories.id"), nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)
    min_quantity = Column(Float, nullable=True)
    max_quantity = Column(Float, nullable=True)
    reorder_point = Column(Float, nullable=True)
    unit_cost = Column(Float, nullable=True)
    location = Column(String(200), nullable=True)
    supplier = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Batch tracking
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(String(20), nullable=True)
    
    # Relationships
    category = relationship("InventoryCategory", back_populates="items")
    transactions = relationship("InventoryTransaction", back_populates="item")
    requisition_items = relationship("InventoryRequisitionItem", back_populates="item")


class TransactionType(str, enum.Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    SCRAP = "scrap"


class InventoryTransaction(Base, BaseModel):
    __tablename__ = "inventory_transactions"
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=True)
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    item = relationship("InventoryItem", back_populates="transactions")


class RequisitionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class RequisitionLineStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class RequisitionPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class InventoryRequisition(Base, BaseModel):
    __tablename__ = "inventory_requisitions"

    requisition_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(RequisitionStatus), default=RequisitionStatus.DRAFT, nullable=False, index=True)
    priority = Column(SQLEnum(RequisitionPriority), default=RequisitionPriority.MEDIUM, nullable=False)
    needed_by = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)

    # Optional workflow references
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)

    # Audit fields
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    fulfilled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    items = relationship(
        "InventoryRequisitionItem",
        back_populates="requisition",
        cascade="all, delete-orphan",
        order_by="InventoryRequisitionItem.id"
    )
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])
    fulfiller = relationship("User", foreign_keys=[fulfilled_by])
    work_order = relationship("WorkOrder")
    production_order = relationship("ProductionOrder")

    @property
    def line_count(self) -> int:
        return len(self.items or [])


class InventoryRequisitionItem(Base, BaseModel):
    __tablename__ = "inventory_requisition_items"

    requisition_id = Column(Integer, ForeignKey("inventory_requisitions.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    requested_quantity = Column(Float, nullable=False)
    approved_quantity = Column(Float, nullable=True)
    fulfilled_quantity = Column(Float, default=0.0, nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(SQLEnum(RequisitionLineStatus), default=RequisitionLineStatus.PENDING, nullable=False)

    # Relationships
    requisition = relationship("InventoryRequisition", back_populates="items")
    item = relationship("InventoryItem", back_populates="requisition_items")
