from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from schemas.quality import (
    QualityInspectionCreate, QualityInspectionUpdate, QualityInspectionResponse,
    NonConformanceReportCreate, NonConformanceReportUpdate, NonConformanceReportResponse,
    QualityStatistics
)
from schemas.common import PaginatedResponse
from services import quality_service

router = APIRouter()


# ==================== STATISTICS ====================

@router.get("/statistics", response_model=QualityStatistics)
async def get_quality_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get quality statistics."""
    return quality_service.get_quality_statistics(db)


# ==================== QUALITY INSPECTION ENDPOINTS ====================

@router.get("/inspections", response_model=PaginatedResponse[QualityInspectionResponse])
async def list_inspections(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    result: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all quality inspections with optional filters."""
    skip = (page - 1) * limit
    inspections = quality_service.get_quality_inspections(
        db, skip=skip, limit=limit, status=status, result=result, search=search
    )
    total = quality_service.get_inspection_count(db, status=status, result=result, search=search)
    
    return PaginatedResponse(
        success=True,
        data=inspections,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/inspections", response_model=QualityInspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    inspection: QualityInspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new quality inspection."""
    return quality_service.create_quality_inspection(db, inspection)


@router.get("/inspections/{inspection_id}", response_model=QualityInspectionResponse)
async def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get quality inspection by ID."""
    inspection = quality_service.get_quality_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return inspection


@router.put("/inspections/{inspection_id}", response_model=QualityInspectionResponse)
async def update_inspection(
    inspection_id: int,
    inspection: QualityInspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update quality inspection."""
    updated = quality_service.update_quality_inspection(db, inspection_id, inspection)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return updated


@router.delete("/inspections/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete quality inspection."""
    deleted = quality_service.delete_quality_inspection(db, inspection_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")


# ==================== NCR ENDPOINTS ====================

@router.get("/ncrs", response_model=PaginatedResponse[NonConformanceReportResponse])
async def list_ncrs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all NCRs with optional filters."""
    skip = (page - 1) * limit
    ncrs = quality_service.get_ncrs(
        db, skip=skip, limit=limit, status=status, severity=severity, search=search
    )
    total = quality_service.get_ncr_count(db, status=status, severity=severity, search=search)
    
    return PaginatedResponse(
        success=True,
        data=ncrs,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/ncrs", response_model=NonConformanceReportResponse, status_code=status.HTTP_201_CREATED)
async def create_ncr(
    ncr: NonConformanceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new NCR."""
    return quality_service.create_ncr(db, ncr)


@router.get("/ncrs/{ncr_id}", response_model=NonConformanceReportResponse)
async def get_ncr(
    ncr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get NCR by ID."""
    ncr = quality_service.get_ncr(db, ncr_id)
    if not ncr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NCR not found")
    return ncr


@router.put("/ncrs/{ncr_id}", response_model=NonConformanceReportResponse)
async def update_ncr(
    ncr_id: int,
    ncr: NonConformanceReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update NCR."""
    updated = quality_service.update_ncr(db, ncr_id, ncr)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NCR not found")
    return updated


@router.delete("/ncrs/{ncr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ncr(
    ncr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete NCR."""
    deleted = quality_service.delete_ncr(db, ncr_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NCR not found")
