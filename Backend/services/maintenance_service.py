from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.maintenance import MaintenanceReport
from schemas.maintenance import MaintenanceReportCreate, MaintenanceReportUpdate


def generate_report_number(db: Session) -> str:
    """Generate unique maintenance report number."""
    count = db.query(MaintenanceReport).count()
    return f"MR-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"


def get_maintenance_statistics(db: Session) -> dict:
    """Get maintenance statistics."""
    total_reports = db.query(func.count(MaintenanceReport.id)).scalar()
    
    reviewed_count = db.query(func.count(MaintenanceReport.id)).filter(
        MaintenanceReport.reviewed_by.isnot(None)
    ).scalar()
    
    pending_review = total_reports - reviewed_count
    
    follow_up_required = db.query(func.count(MaintenanceReport.id)).filter(
        MaintenanceReport.follow_up_required == True
    ).scalar()
    
    equipment_operational = db.query(func.count(MaintenanceReport.id)).filter(
        MaintenanceReport.equipment_operational == True
    ).scalar()
    
    total_labor_hours = db.query(
        func.sum(MaintenanceReport.labor_hours)
    ).scalar() or 0
    
    return {
        "total_reports": total_reports,
        "reviewed_count": reviewed_count,
        "pending_review": pending_review,
        "follow_up_required": follow_up_required,
        "equipment_operational": equipment_operational,
        "total_labor_hours": float(total_labor_hours)
    }


def get_reports_count(db: Session, search: Optional[str] = None,
                     equipment_id: Optional[int] = None,
                     craftsman_id: Optional[int] = None) -> int:
    """Get count of maintenance reports with filters."""
    query = db.query(func.count(MaintenanceReport.id))
    
    if search:
        query = query.filter(
            or_(
                MaintenanceReport.report_number.ilike(f"%{search}%"),
                MaintenanceReport.work_performed.ilike(f"%{search}%"),
                MaintenanceReport.findings.ilike(f"%{search}%")
            )
        )
    
    if equipment_id:
        query = query.filter(MaintenanceReport.equipment_id == equipment_id)
    
    if craftsman_id:
        query = query.filter(MaintenanceReport.craftsman_id == craftsman_id)
    
    return query.scalar()


def get_maintenance_reports(db: Session, skip: int = 0, limit: int = 100,
                            search: Optional[str] = None,
                            equipment_id: Optional[int] = None,
                            craftsman_id: Optional[int] = None) -> List[MaintenanceReport]:
    """Get all maintenance reports with optional filters."""
    query = db.query(MaintenanceReport)
    
    if search:
        query = query.filter(
            or_(
                MaintenanceReport.report_number.ilike(f"%{search}%"),
                MaintenanceReport.work_performed.ilike(f"%{search}%"),
                MaintenanceReport.findings.ilike(f"%{search}%")
            )
        )
    
    if equipment_id:
        query = query.filter(MaintenanceReport.equipment_id == equipment_id)
    
    if craftsman_id:
        query = query.filter(MaintenanceReport.craftsman_id == craftsman_id)
    
    return query.order_by(MaintenanceReport.created_at.desc()).offset(skip).limit(limit).all()


def get_maintenance_report(db: Session, report_id: int) -> Optional[MaintenanceReport]:
    """Get maintenance report by ID."""
    return db.query(MaintenanceReport).filter(MaintenanceReport.id == report_id).first()


def get_maintenance_report_by_number(db: Session, report_number: str) -> Optional[MaintenanceReport]:
    """Get maintenance report by number."""
    return db.query(MaintenanceReport).filter(MaintenanceReport.report_number == report_number).first()


def create_maintenance_report(db: Session, report: MaintenanceReportCreate) -> MaintenanceReport:
    """Create new maintenance report."""
    # Generate report number
    report_number = generate_report_number(db)
    
    db_report = MaintenanceReport(
        report_number=report_number,
        completed_at=datetime.now().isoformat(),
        **report.model_dump()
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def update_maintenance_report(db: Session, report_id: int, report: MaintenanceReportUpdate) -> Optional[MaintenanceReport]:
    """Update maintenance report."""
    db_report = get_maintenance_report(db, report_id)
    if not db_report:
        return None
    
    update_data = report.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


def delete_maintenance_report(db: Session, report_id: int) -> bool:
    """Delete maintenance report."""
    db_report = get_maintenance_report(db, report_id)
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True


def review_maintenance_report(db: Session, report_id: int, reviewer_id: int) -> Optional[MaintenanceReport]:
    """Mark maintenance report as reviewed."""
    db_report = get_maintenance_report(db, report_id)
    if not db_report:
        return None
    
    db_report.reviewed_by = reviewer_id
    db_report.reviewed_at = datetime.now().isoformat()
    
    db.commit()
    db.refresh(db_report)
    return db_report


def get_work_order_reports(db: Session, work_order_id: int) -> List[MaintenanceReport]:
    """Get maintenance reports for a work order."""
    return db.query(MaintenanceReport).filter(
        MaintenanceReport.work_order_id == work_order_id
    ).order_by(MaintenanceReport.created_at.desc()).all()


def get_equipment_maintenance_history(db: Session, equipment_id: int) -> List[MaintenanceReport]:
    """Get maintenance history for an equipment."""
    return db.query(MaintenanceReport).filter(
        MaintenanceReport.equipment_id == equipment_id
    ).order_by(MaintenanceReport.created_at.desc()).all()


def get_craftsman_reports(db: Session, craftsman_id: int) -> List[MaintenanceReport]:
    """Get maintenance reports by a craftsman."""
    return db.query(MaintenanceReport).filter(
        MaintenanceReport.craftsman_id == craftsman_id
    ).order_by(MaintenanceReport.created_at.desc()).all()
