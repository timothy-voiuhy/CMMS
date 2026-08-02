from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from schemas.maintenance import MaintenanceReportCreate, MaintenanceReportUpdate, MaintenanceReportResponse
from schemas.common import PaginatedResponse
from services import maintenance_service

router = APIRouter()


@router.get("/statistics")
async def get_maintenance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance statistics."""
    return maintenance_service.get_maintenance_statistics(db)


@router.get("/reports", response_model=PaginatedResponse[MaintenanceReportResponse])
async def list_maintenance_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    equipment_id: Optional[int] = None,
    craftsman_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all maintenance reports with optional filters."""
    skip = (page - 1) * limit
    reports = maintenance_service.get_maintenance_reports(
        db, skip=skip, limit=limit, search=search,
        equipment_id=equipment_id, craftsman_id=craftsman_id
    )
    total = maintenance_service.get_reports_count(
        db, search=search, equipment_id=equipment_id, craftsman_id=craftsman_id
    )
    
    return PaginatedResponse(
        success=True,
        data=reports,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/reports", response_model=MaintenanceReportResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_report(
    report: MaintenanceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new maintenance report."""
    return maintenance_service.create_maintenance_report(db, report)


@router.get("/reports/{report_id}", response_model=MaintenanceReportResponse)
async def get_maintenance_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance report by ID."""
    report = maintenance_service.get_maintenance_report(db, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")
    return report


@router.put("/reports/{report_id}", response_model=MaintenanceReportResponse)
async def update_maintenance_report(
    report_id: int,
    report: MaintenanceReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update maintenance report."""
    updated = maintenance_service.update_maintenance_report(db, report_id, report)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")
    return updated


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete maintenance report."""
    deleted = maintenance_service.delete_maintenance_report(db, report_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")


@router.post("/reports/{report_id}/review", response_model=MaintenanceReportResponse)
async def review_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark maintenance report as reviewed."""
    report = maintenance_service.review_maintenance_report(db, report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")
    return report


@router.get("/reports/by-work-order/{work_order_id}", response_model=List[MaintenanceReportResponse])
async def get_work_order_reports(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance reports for a work order."""
    return maintenance_service.get_work_order_reports(db, work_order_id)


@router.get("/reports/by-equipment/{equipment_id}", response_model=List[MaintenanceReportResponse])
async def get_equipment_history(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance history for an equipment."""
    return maintenance_service.get_equipment_maintenance_history(db, equipment_id)


@router.get("/reports/by-craftsman/{craftsman_id}", response_model=List[MaintenanceReportResponse])
async def get_craftsman_reports(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance reports by a craftsman."""
    return maintenance_service.get_craftsman_reports(db, craftsman_id)
