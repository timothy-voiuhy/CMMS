from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from schemas.craftsman import (
    CraftsmanCreate, CraftsmanUpdate, CraftsmanResponse, CraftsmanWithUser,
    SkillCreate, SkillResponse, CraftsmanWithUserCreate
)
from schemas.common import PaginatedResponse
from services import craftsman_service
import math

router = APIRouter()


@router.get("/statistics")
async def get_craftsman_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get craftsman statistics."""
    return craftsman_service.get_craftsman_statistics(db)


@router.get("/", response_model=PaginatedResponse[CraftsmanWithUser])
async def list_craftsmen(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all craftsmen."""
    skip = (page - 1) * limit
    
    # Get total count
    total = craftsman_service.get_craftsmen_count(db, search=search)
    
    # Get craftsmen list
    craftsmen = craftsman_service.get_craftsmen(db, skip=skip, limit=limit, search=search)
    
    # Enrich with user data and role
    result = []
    for craftsman in craftsmen:
        role_name = craftsman.role.name if craftsman.role else None
        result.append(CraftsmanWithUser(
            **craftsman.__dict__,
            username=craftsman.user.username,
            email=craftsman.user.email,
            full_name=craftsman.user.full_name,
            phone=craftsman.user.phone,
            role_name=role_name
        ))
    
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    
    return PaginatedResponse(
        success=True,
        data=result,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=total_pages
    )


@router.post("/", response_model=CraftsmanResponse, status_code=status.HTTP_201_CREATED)
async def create_craftsman(
    craftsman: CraftsmanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new craftsman (requires existing user)."""
    return craftsman_service.create_craftsman(db, craftsman)


@router.post("/with-user", response_model=CraftsmanWithUser, status_code=status.HTTP_201_CREATED)
async def create_craftsman_with_user(
    data: CraftsmanWithUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new user and craftsman profile together."""
    craftsman = craftsman_service.create_craftsman_with_user(
        db=db,
        full_name=data.full_name,
        username=data.username,
        email=data.email,
        password=data.password,
        phone=data.phone,
        employee_id=data.employee_id,
        department=data.department,
        position=data.position,
        role_id=data.role_id,
        hire_date=data.hire_date,
        certification_level=data.certification_level,
        hourly_rate=data.hourly_rate,
        notes=data.notes
    )
    
    role_name = craftsman.role.name if craftsman.role else None
    return CraftsmanWithUser(
        **craftsman.__dict__,
        username=craftsman.user.username,
        email=craftsman.user.email,
        full_name=craftsman.user.full_name,
        phone=craftsman.user.phone,
        role_name=role_name
    )


@router.get("/{craftsman_id}", response_model=CraftsmanWithUser)
async def get_craftsman(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a craftsman by ID."""
    craftsman = craftsman_service.get_craftsman(db, craftsman_id)
    if not craftsman:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")
    
    role_name = craftsman.role.name if craftsman.role else None
    return CraftsmanWithUser(
        **craftsman.__dict__,
        username=craftsman.user.username,
        email=craftsman.user.email,
        full_name=craftsman.user.full_name,
        phone=craftsman.user.phone,
        role_name=role_name
    )


@router.get("/{craftsman_id}/statistics")
async def get_craftsman_individual_statistics(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get individual craftsman statistics."""
    craftsman = craftsman_service.get_craftsman(db, craftsman_id)
    if not craftsman:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")
    
    return craftsman_service.get_individual_craftsman_statistics(db, craftsman_id)


@router.get("/{craftsman_id}/equipment")
async def get_craftsman_equipment(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment operated by craftsman."""
    craftsman = craftsman_service.get_craftsman(db, craftsman_id)
    if not craftsman:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")
    
    return craftsman_service.get_craftsman_equipment(db, craftsman_id)


@router.get("/{craftsman_id}/work-orders")
async def get_craftsman_work_orders(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work orders assigned to craftsman."""
    craftsman = craftsman_service.get_craftsman(db, craftsman_id)
    if not craftsman:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")
    
    return craftsman_service.get_craftsman_work_orders(db, craftsman_id)


@router.put("/{craftsman_id}", response_model=CraftsmanWithUser)
async def update_craftsman(
    craftsman_id: int,
    craftsman: CraftsmanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a craftsman."""
    updated = craftsman_service.update_craftsman(db, craftsman_id, craftsman)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")
    
    role_name = updated.role.name if updated.role else None
    return CraftsmanWithUser(
        **updated.__dict__,
        username=updated.user.username,
        email=updated.user.email,
        full_name=updated.user.full_name,
        phone=updated.user.phone,
        role_name=role_name
    )


@router.delete("/{craftsman_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_craftsman(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a craftsman."""
    deleted = craftsman_service.delete_craftsman(db, craftsman_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")


@router.post("/{craftsman_id}/skills/{skill_id}", response_model=CraftsmanResponse)
async def add_skill(
    craftsman_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a skill to a craftsman."""
    craftsman = craftsman_service.add_skill_to_craftsman(db, craftsman_id, skill_id)
    if not craftsman:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")
    return craftsman


@router.delete("/{craftsman_id}/skills/{skill_id}", response_model=CraftsmanResponse)
async def remove_skill(
    craftsman_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a skill from a craftsman."""
    craftsman = craftsman_service.remove_skill_from_craftsman(db, craftsman_id, skill_id)
    if not craftsman:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Craftsman not found")
    return craftsman


# Skills endpoints
@router.get("/skills/all", response_model=List[SkillResponse])
async def list_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all skills."""
    return craftsman_service.get_skills(db, skip=skip, limit=limit)


@router.post("/skills/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new skill."""
    return craftsman_service.create_skill(db, skill.name, skill.description, skill.category)



@router.get("/metadata/departments", response_model=List[str])
async def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of unique departments from existing craftsmen."""
    return craftsman_service.get_distinct_departments(db)


@router.get("/metadata/positions", response_model=List[str])
async def get_positions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of unique positions from existing craftsmen."""
    return craftsman_service.get_distinct_positions(db)
