from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from models.equipment import EquipmentStatus
from schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentResponse
from schemas.common import PaginatedResponse
from services import equipment_service
import math

router = APIRouter()


@router.get("/statistics")
async def get_equipment_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment statistics."""
    return equipment_service.get_equipment_statistics(db)


@router.get("/", response_model=PaginatedResponse[EquipmentResponse])
async def list_equipment(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[EquipmentStatus] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all equipment with optional filters."""
    skip = (page - 1) * limit
    
    # Get total count with filters
    total = equipment_service.get_equipment_count(
        db, search=search, status_filter=status, category=category
    )
    
    # Get equipment list
    equipment_list = equipment_service.get_equipment_list(
        db, skip=skip, limit=limit, search=search, 
        status_filter=status, category=category
    )
    
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    
    return PaginatedResponse(
        success=True,
        data=equipment_list,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=total_pages
    )


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new equipment."""
    return equipment_service.create_equipment(db, equipment)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment by ID."""
    equipment = equipment_service.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    return equipment


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: int,
    equipment: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update equipment."""
    updated = equipment_service.update_equipment(db, equipment_id, equipment)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    return updated


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete equipment."""
    deleted = equipment_service.delete_equipment(db, equipment_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")


@router.get("/{equipment_id}/children", response_model=List[EquipmentResponse])
async def get_equipment_children(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get child equipment."""
    equipment = equipment_service.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    
    return equipment_service.get_equipment_children(db, equipment_id)


@router.get("/by-code/{equipment_code}", response_model=EquipmentResponse)
async def get_equipment_by_code(
    equipment_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment by equipment code."""
    equipment = equipment_service.get_equipment_by_code(db, equipment_code)
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    return equipment
