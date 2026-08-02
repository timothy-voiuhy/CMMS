from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel
import enum


class WorkOrderType(str, enum.Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    EMERGENCY = "emergency"
    MODIFICATION = "modification"
    INSPECTION = "inspection"


class WorkOrderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrder(Base, BaseModel):
    __tablename__ = "work_orders"
    
    work_order_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    work_order_type = Column(SQLEnum(WorkOrderType), nullable=False)
    priority = Column(SQLEnum(WorkOrderPriority), default=WorkOrderPriority.MEDIUM, nullable=False)
    status = Column(SQLEnum(WorkOrderStatus), default=WorkOrderStatus.PENDING, nullable=False)
    
    # Equipment reference
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("craftsmen.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dates
    scheduled_date = Column(String(20), nullable=True)
    due_date = Column(String(20), nullable=True)
    started_at = Column(String(30), nullable=True)
    completed_at = Column(String(30), nullable=True)
    
    # Time tracking
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="work_orders")
    craftsman = relationship("Craftsman", back_populates="work_orders", foreign_keys=[assigned_to])
    creator = relationship("User", back_populates="work_orders_created", foreign_keys=[created_by])
    maintenance_reports = relationship("MaintenanceReport", back_populates="work_order")
