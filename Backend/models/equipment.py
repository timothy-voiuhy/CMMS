from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel
from models.craftsman import equipment_operators
import enum


class EquipmentStatus(str, enum.Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    BREAKDOWN = "breakdown"
    RETIRED = "retired"


class Equipment(Base, BaseModel):
    __tablename__ = "equipment"
    
    name = Column(String(200), nullable=False)
    equipment_id = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    status = Column(SQLEnum(EquipmentStatus), default=EquipmentStatus.OPERATIONAL, nullable=False)
    purchase_date = Column(String(20), nullable=True)
    warranty_expiry = Column(String(20), nullable=True)
    specifications = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Parent-child relationship (hierarchical equipment structure)
    parent_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    parent = relationship("Equipment", remote_side="Equipment.id", backref="children")
    
    # Relationships
    work_orders = relationship("WorkOrder", back_populates="equipment")
    maintenance_reports = relationship("MaintenanceReport", back_populates="equipment")
    operators = relationship("Craftsman", secondary=equipment_operators, back_populates="operated_equipment")
