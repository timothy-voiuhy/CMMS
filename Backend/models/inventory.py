from sqlalchemy import Column, Integer, String, Float, Text, Enum as SQLEnum, ForeignKey, Boolean
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
