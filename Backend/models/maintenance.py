from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel


class MaintenanceReport(Base, BaseModel):
    __tablename__ = "maintenance_reports"
    
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    craftsman_id = Column(Integer, ForeignKey("craftsmen.id"), nullable=False)
    
    # Report details
    report_number = Column(String(100), unique=True, index=True, nullable=False)
    work_performed = Column(Text, nullable=False)
    findings = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Parts used
    parts_used = Column(Text, nullable=True)
    
    # Labor
    labor_hours = Column(Integer, nullable=True)
    
    # Status
    equipment_operational = Column(Boolean, default=True, nullable=False)
    follow_up_required = Column(Boolean, default=False, nullable=False)
    
    # Attachments (stored as JSON array of file paths)
    attachments = Column(Text, nullable=True)
    
    # Sign-off
    completed_at = Column(String(30), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(String(30), nullable=True)
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="maintenance_reports")
    equipment = relationship("Equipment", back_populates="maintenance_reports")
    craftsman = relationship("Craftsman", back_populates="maintenance_reports")
