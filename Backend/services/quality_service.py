from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime
from models.quality import (
    QualityInspection, QualityInspectionItem, NonConformanceReport,
    InspectionStatus, InspectionResult, NCRStatus
)
from schemas.quality import (
    QualityInspectionCreate, QualityInspectionUpdate,
    NonConformanceReportCreate, NonConformanceReportUpdate
)


# ==================== QUALITY INSPECTION SERVICES ====================

def generate_inspection_number(db: Session) -> str:
    """Generate unique inspection number."""
    last_inspection = db.query(QualityInspection).order_by(QualityInspection.id.desc()).first()
    if last_inspection and last_inspection.inspection_number:
        try:
            last_num = int(last_inspection.inspection_number.split('-')[1])
            return f"QI-{last_num + 1:06d}"
        except:
            pass
    return "QI-000001"


def get_quality_inspections(
    db: Session, skip: int = 0, limit: int = 100,
    status: Optional[str] = None,
    result: Optional[str] = None,
    search: Optional[str] = None
) -> List[QualityInspection]:
    """Get all quality inspections with filters."""
    query = db.query(QualityInspection).options(
        joinedload(QualityInspection.inspection_items),
        joinedload(QualityInspection.inspector)
    )
    
    if status:
        query = query.filter(QualityInspection.status == status)
    if result:
        query = query.filter(QualityInspection.result == result)
    if search:
        query = query.filter(
            (QualityInspection.inspection_number.ilike(f"%{search}%")) |
            (QualityInspection.product_name.ilike(f"%{search}%")) |
            (QualityInspection.batch_number.ilike(f"%{search}%"))
        )
    
    return query.order_by(QualityInspection.created_at.desc()).offset(skip).limit(limit).all()


def get_inspection_count(
    db: Session,
    status: Optional[str] = None,
    result: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """Get count of inspections with filters."""
    query = db.query(func.count(QualityInspection.id))
    
    if status:
        query = query.filter(QualityInspection.status == status)
    if result:
        query = query.filter(QualityInspection.result == result)
    if search:
        query = query.filter(
            (QualityInspection.inspection_number.ilike(f"%{search}%")) |
            (QualityInspection.product_name.ilike(f"%{search}%")) |
            (QualityInspection.batch_number.ilike(f"%{search}%"))
        )
    
    return query.scalar()


def get_quality_inspection(db: Session, inspection_id: int) -> Optional[QualityInspection]:
    """Get quality inspection by ID."""
    return db.query(QualityInspection).options(
        joinedload(QualityInspection.inspection_items),
        joinedload(QualityInspection.inspector),
        joinedload(QualityInspection.production_order),
        joinedload(QualityInspection.ncrs)
    ).filter(QualityInspection.id == inspection_id).first()


def create_quality_inspection(db: Session, inspection: QualityInspectionCreate) -> QualityInspection:
    """Create new quality inspection."""
    inspection_number = generate_inspection_number(db)
    
    db_inspection = QualityInspection(
        inspection_number=inspection_number,
        **inspection.model_dump(exclude={'inspection_items'})
    )
    db.add(db_inspection)
    db.flush()
    
    # Add inspection items
    for item in inspection.inspection_items:
        db_item = QualityInspectionItem(
            inspection_id=db_inspection.id,
            **item.model_dump()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


def update_quality_inspection(
    db: Session,
    inspection_id: int,
    inspection: QualityInspectionUpdate
) -> Optional[QualityInspection]:
    """Update quality inspection."""
    db_inspection = get_quality_inspection(db, inspection_id)
    if not db_inspection:
        return None
    
    update_data = inspection.model_dump(exclude_unset=True)
    
    # If status is being set to completed, set completed_at
    if 'status' in update_data and update_data['status'] == InspectionStatus.COMPLETED:
        update_data['completed_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_inspection, field, value)
    
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


def delete_quality_inspection(db: Session, inspection_id: int) -> bool:
    """Delete quality inspection."""
    db_inspection = get_quality_inspection(db, inspection_id)
    if not db_inspection:
        return False
    
    db.delete(db_inspection)
    db.commit()
    return True


# ==================== NCR SERVICES ====================

def generate_ncr_number(db: Session) -> str:
    """Generate unique NCR number."""
    last_ncr = db.query(NonConformanceReport).order_by(NonConformanceReport.id.desc()).first()
    if last_ncr and last_ncr.ncr_number:
        try:
            last_num = int(last_ncr.ncr_number.split('-')[1])
            return f"NCR-{last_num + 1:06d}"
        except:
            pass
    return "NCR-000001"


def get_ncrs(
    db: Session, skip: int = 0, limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None
) -> List[NonConformanceReport]:
    """Get all NCRs with filters."""
    query = db.query(NonConformanceReport).options(
        joinedload(NonConformanceReport.reported_by),
        joinedload(NonConformanceReport.assigned_to)
    )
    
    if status:
        query = query.filter(NonConformanceReport.status == status)
    if severity:
        query = query.filter(NonConformanceReport.severity == severity)
    if search:
        query = query.filter(
            (NonConformanceReport.ncr_number.ilike(f"%{search}%")) |
            (NonConformanceReport.title.ilike(f"%{search}%")) |
            (NonConformanceReport.description.ilike(f"%{search}%"))
        )
    
    return query.order_by(NonConformanceReport.created_at.desc()).offset(skip).limit(limit).all()


def get_ncr_count(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """Get count of NCRs with filters."""
    query = db.query(func.count(NonConformanceReport.id))
    
    if status:
        query = query.filter(NonConformanceReport.status == status)
    if severity:
        query = query.filter(NonConformanceReport.severity == severity)
    if search:
        query = query.filter(
            (NonConformanceReport.ncr_number.ilike(f"%{search}%")) |
            (NonConformanceReport.title.ilike(f"%{search}%")) |
            (NonConformanceReport.description.ilike(f"%{search}%"))
        )
    
    return query.scalar()


def get_ncr(db: Session, ncr_id: int) -> Optional[NonConformanceReport]:
    """Get NCR by ID."""
    return db.query(NonConformanceReport).options(
        joinedload(NonConformanceReport.reported_by),
        joinedload(NonConformanceReport.assigned_to),
        joinedload(NonConformanceReport.inspection),
        joinedload(NonConformanceReport.production_order),
        joinedload(NonConformanceReport.equipment)
    ).filter(NonConformanceReport.id == ncr_id).first()


def create_ncr(db: Session, ncr: NonConformanceReportCreate) -> NonConformanceReport:
    """Create new NCR."""
    ncr_number = generate_ncr_number(db)
    
    db_ncr = NonConformanceReport(
        ncr_number=ncr_number,
        **ncr.model_dump()
    )
    db.add(db_ncr)
    db.commit()
    db.refresh(db_ncr)
    return db_ncr


def update_ncr(
    db: Session,
    ncr_id: int,
    ncr: NonConformanceReportUpdate
) -> Optional[NonConformanceReport]:
    """Update NCR."""
    db_ncr = get_ncr(db, ncr_id)
    if not db_ncr:
        return None
    
    update_data = ncr.model_dump(exclude_unset=True)
    
    # If status is being set to closed, set closed_at
    if 'status' in update_data and update_data['status'] == NCRStatus.CLOSED:
        update_data['closed_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_ncr, field, value)
    
    db.commit()
    db.refresh(db_ncr)
    return db_ncr


def delete_ncr(db: Session, ncr_id: int) -> bool:
    """Delete NCR."""
    db_ncr = get_ncr(db, ncr_id)
    if not db_ncr:
        return False
    
    db.delete(db_ncr)
    db.commit()
    return True


# ==================== STATISTICS SERVICES ====================

def get_quality_statistics(db: Session) -> dict:
    """Get quality statistics."""
    total_inspections = db.query(func.count(QualityInspection.id)).scalar()
    pending_inspections = db.query(func.count(QualityInspection.id)).filter(
        QualityInspection.status == InspectionStatus.PENDING
    ).scalar()
    completed_inspections = db.query(func.count(QualityInspection.id)).filter(
        QualityInspection.status == InspectionStatus.COMPLETED
    ).scalar()
    
    passed_inspections = db.query(func.count(QualityInspection.id)).filter(
        QualityInspection.result == InspectionResult.PASS
    ).scalar()
    failed_inspections = db.query(func.count(QualityInspection.id)).filter(
        QualityInspection.result == InspectionResult.FAIL
    ).scalar()
    
    pass_rate = (passed_inspections / total_inspections * 100) if total_inspections > 0 else 0
    fail_rate = (failed_inspections / total_inspections * 100) if total_inspections > 0 else 0
    
    total_ncrs = db.query(func.count(NonConformanceReport.id)).scalar()
    open_ncrs = db.query(func.count(NonConformanceReport.id)).filter(
        NonConformanceReport.status.in_([NCRStatus.OPEN, NCRStatus.INVESTIGATING, NCRStatus.CORRECTIVE_ACTION])
    ).scalar()
    critical_ncrs = db.query(func.count(NonConformanceReport.id)).filter(
        and_(
            NonConformanceReport.severity == "critical",
            NonConformanceReport.status != NCRStatus.CLOSED
        )
    ).scalar()
    
    avg_defects = db.query(func.avg(QualityInspection.defects_found)).scalar() or 0
    
    return {
        "total_inspections": total_inspections or 0,
        "pending_inspections": pending_inspections or 0,
        "completed_inspections": completed_inspections or 0,
        "pass_rate": round(pass_rate, 2),
        "fail_rate": round(fail_rate, 2),
        "total_ncrs": total_ncrs or 0,
        "open_ncrs": open_ncrs or 0,
        "critical_ncrs": critical_ncrs or 0,
        "avg_defects_per_inspection": round(avg_defects, 2)
    }
