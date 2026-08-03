from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from db.base import Base


class InspectionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class InspectionResult(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    PENDING = "pending"


class NCRStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CORRECTIVE_ACTION = "corrective_action"
    CLOSED = "closed"
    REJECTED = "rejected"


class NCRSeverity(str, enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class QualityInspection(Base):
    """Quality inspection record for products/batches."""
    __tablename__ = "quality_inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Reference
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    batch_number = Column(String(100), nullable=True)
    product_name = Column(String(200), nullable=False)
    
    # Inspection details
    inspection_type = Column(String(100), nullable=False)  # Incoming, In-Process, Final, etc.
    inspection_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Criteria
    sample_size = Column(Integer, nullable=True)
    defects_found = Column(Integer, default=0)
    specifications = Column(Text, nullable=True)  # JSON string
    
    # Results
    status = Column(SQLEnum(InspectionStatus), default=InspectionStatus.PENDING, nullable=False)
    result = Column(SQLEnum(InspectionResult), default=InspectionResult.PENDING, nullable=False)
    pass_rate = Column(Float, nullable=True)  # Percentage
    
    # Details
    observations = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    inspector = relationship("User", foreign_keys=[inspector_id])
    production_order = relationship("ProductionOrder", back_populates="quality_inspections")
    inspection_items = relationship("QualityInspectionItem", back_populates="inspection", cascade="all, delete-orphan")
    ncrs = relationship("NonConformanceReport", back_populates="inspection")


class QualityInspectionItem(Base):
    """Individual inspection criteria/checkpoints."""
    __tablename__ = "quality_inspection_items"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("quality_inspections.id"), nullable=False)
    
    checkpoint_name = Column(String(200), nullable=False)
    specification = Column(String(500), nullable=True)
    measured_value = Column(String(200), nullable=True)
    result = Column(SQLEnum(InspectionResult), default=InspectionResult.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    inspection = relationship("QualityInspection", back_populates="inspection_items")


class NonConformanceReport(Base):
    """Non-conformance report for quality issues."""
    __tablename__ = "non_conformance_reports"

    id = Column(Integer, primary_key=True, index=True)
    ncr_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Reference
    inspection_id = Column(Integer, ForeignKey("quality_inspections.id"), nullable=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    batch_number = Column(String(100), nullable=True)
    
    # Issue details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(NCRSeverity), default=NCRSeverity.MINOR, nullable=False)
    status = Column(SQLEnum(NCRStatus), default=NCRStatus.OPEN, nullable=False)
    
    # People
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Analysis
    root_cause = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    preventive_action = Column(Text, nullable=True)
    
    # Cost impact
    estimated_cost = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    inspection = relationship("QualityInspection", back_populates="ncrs")
    production_order = relationship("ProductionOrder", back_populates="ncrs")
    equipment = relationship("Equipment")
    reported_by = relationship("User", foreign_keys=[reported_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])


class QualityMetric(Base):
    """Aggregate quality metrics by period."""
    __tablename__ = "quality_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metrics
    total_inspections = Column(Integer, default=0)
    passed_inspections = Column(Integer, default=0)
    failed_inspections = Column(Integer, default=0)
    pass_rate = Column(Float, default=0.0)  # Percentage
    
    total_ncrs = Column(Integer, default=0)
    open_ncrs = Column(Integer, default=0)
    closed_ncrs = Column(Integer, default=0)
    
    defect_rate = Column(Float, default=0.0)  # Per thousand units
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
