from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel
import enum


class ShiftType(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"
    ROTATING = "rotating"


class ProductionLineStatus(str, enum.Enum):
    ACTIVE = "active"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class ProductionOrderStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionLine(Base, BaseModel):
    __tablename__ = "production_lines"
    
    line_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProductionLineStatus), default=ProductionLineStatus.IDLE, nullable=False)
    
    # Capacity
    capacity_per_hour = Column(Float, nullable=True)
    capacity_unit = Column(String(50), nullable=True)
    
    # Location
    location = Column(String(200), nullable=True)
    floor = Column(String(50), nullable=True)
    
    # Relationships
    shifts = relationship("Shift", back_populates="production_line", cascade="all, delete-orphan")
    production_orders = relationship("ProductionOrder", back_populates="production_line")
    equipment_stations = relationship("ProductionLineEquipment", back_populates="production_line", cascade="all, delete-orphan", order_by="ProductionLineEquipment.sequence_order")


class ProductionLineEquipment(Base, BaseModel):
    __tablename__ = "production_line_equipment"
    
    production_line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    
    # Process order - defines the sequence in the production flow
    sequence_order = Column(Integer, nullable=False)
    
    # Station information
    station_name = Column(String(100), nullable=True)  # e.g., "Cutting Station", "Assembly Station"
    
    # Operators assigned to this equipment on the line
    operators = Column(JSON, nullable=True)  # List of craftsman IDs
    
    # Optional configuration
    cycle_time_minutes = Column(Float, nullable=True)  # Expected time for this station
    notes = Column(Text, nullable=True)
    
    # Relationships
    production_line = relationship("ProductionLine", back_populates="equipment_stations")
    equipment = relationship("Equipment")


class Shift(Base, BaseModel):
    __tablename__ = "shifts"
    
    production_line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=False)
    shift_type = Column(SQLEnum(ShiftType), nullable=False)
    
    # Time
    start_time = Column(String(10), nullable=False)  # HH:MM format
    end_time = Column(String(10), nullable=False)
    
    # Team
    team_leader_id = Column(Integer, ForeignKey("craftsmen.id"), nullable=True)
    operators = Column(JSON, nullable=True)  # List of craftsman IDs
    
    # Days
    active_days = Column(JSON, nullable=True)  # List of day numbers (0=Monday, 6=Sunday)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    production_line = relationship("ProductionLine", back_populates="shifts")
    team_leader = relationship("Craftsman", foreign_keys=[team_leader_id])


class ProductionOrder(Base, BaseModel):
    __tablename__ = "production_orders"
    
    order_number = Column(String(100), unique=True, index=True, nullable=False)
    production_line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=False)
    
    # Product
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(100), nullable=True)
    
    # Quantity
    target_quantity = Column(Float, nullable=False)
    produced_quantity = Column(Float, default=0.0, nullable=False)
    unit = Column(String(50), nullable=False)
    
    # Quality
    defect_quantity = Column(Float, default=0.0, nullable=True)
    
    # Status
    status = Column(SQLEnum(ProductionOrderStatus), default=ProductionOrderStatus.PENDING, nullable=False)
    priority = Column(Integer, default=3, nullable=False)  # 1=Urgent, 5=Low
    
    # Schedule
    scheduled_start = Column(String(30), nullable=True)
    scheduled_end = Column(String(30), nullable=True)
    actual_start = Column(String(30), nullable=True)
    actual_end = Column(String(30), nullable=True)
    
    # Assignment
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    # Relationships
    production_line = relationship("ProductionLine", back_populates="production_orders")
    shift = relationship("Shift")
    supervisor = relationship("User")


class PackagingOrder(Base, BaseModel):
    __tablename__ = "packaging_orders"
    
    order_number = Column(String(100), unique=True, index=True, nullable=False)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    
    # Product
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(100), nullable=True)
    
    # Quantity
    target_quantity = Column(Float, nullable=False)
    packaged_quantity = Column(Float, default=0.0, nullable=False)
    unit = Column(String(50), nullable=False)
    
    # Packaging
    packaging_type = Column(String(100), nullable=True)
    packaging_material = Column(String(200), nullable=True)
    units_per_package = Column(Float, nullable=True)
    
    # Status
    status = Column(SQLEnum(ProductionOrderStatus), default=ProductionOrderStatus.PENDING, nullable=False)
    
    # Schedule
    scheduled_start = Column(String(30), nullable=True)
    scheduled_end = Column(String(30), nullable=True)
    actual_start = Column(String(30), nullable=True)
    actual_end = Column(String(30), nullable=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("craftsmen.id"), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    production_order = relationship("ProductionOrder")
    assigned_craftsman = relationship("Craftsman", foreign_keys=[assigned_to])
