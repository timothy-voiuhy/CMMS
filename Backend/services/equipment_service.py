from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from models.equipment import Equipment, EquipmentStatus
from models.craftsman import Craftsman
from schemas.equipment import EquipmentCreate, EquipmentUpdate


def get_equipment_list(db: Session, skip: int = 0, limit: int = 100, 
                       search: Optional[str] = None, 
                       status_filter: Optional[EquipmentStatus] = None,
                       category: Optional[str] = None) -> List[Equipment]:
    """Get all equipment with optional filters."""
    query = db.query(Equipment)
    
    if search:
        query = query.filter(
            or_(
                Equipment.name.ilike(f"%{search}%"),
                Equipment.equipment_id.ilike(f"%{search}%"),
                Equipment.manufacturer.ilike(f"%{search}%"),
                Equipment.location.ilike(f"%{search}%")
            )
        )
    
    if status_filter:
        query = query.filter(Equipment.status == status_filter)
    
    if category:
        query = query.filter(Equipment.category.ilike(f"%{category}%"))
    
    return query.offset(skip).limit(limit).all()


def get_equipment_count(db: Session, search: Optional[str] = None, 
                       status_filter: Optional[EquipmentStatus] = None,
                       category: Optional[str] = None) -> int:
    """Get total count of equipment with optional filters."""
    query = db.query(Equipment)
    
    if search:
        query = query.filter(
            or_(
                Equipment.name.ilike(f"%{search}%"),
                Equipment.equipment_id.ilike(f"%{search}%"),
                Equipment.manufacturer.ilike(f"%{search}%"),
                Equipment.location.ilike(f"%{search}%")
            )
        )
    
    if status_filter:
        query = query.filter(Equipment.status == status_filter)
    
    if category:
        query = query.filter(Equipment.category.ilike(f"%{category}%"))
    
    return query.count()


def get_equipment(db: Session, equipment_id: int) -> Optional[Equipment]:
    """Get equipment by ID."""
    return db.query(Equipment).filter(Equipment.id == equipment_id).first()


def get_equipment_by_code(db: Session, equipment_code: str) -> Optional[Equipment]:
    """Get equipment by equipment_id code."""
    return db.query(Equipment).filter(Equipment.equipment_id == equipment_code).first()


def create_equipment(db: Session, equipment: EquipmentCreate) -> Equipment:
    """Create new equipment."""
    # Check if equipment_id is unique
    existing = get_equipment_by_code(db, equipment.equipment_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment ID already exists"
        )
    
    # Verify parent exists if specified
    if equipment.parent_id:
        parent = get_equipment(db, equipment.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent equipment not found"
            )
    
    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


def update_equipment(db: Session, equipment_id: int, equipment: EquipmentUpdate) -> Optional[Equipment]:
    """Update equipment."""
    db_equipment = get_equipment(db, equipment_id)
    if not db_equipment:
        return None
    
    update_data = equipment.model_dump(exclude_unset=True)
    
    # Verify parent exists if being updated
    if 'parent_id' in update_data and update_data['parent_id']:
        parent = get_equipment(db, update_data['parent_id'])
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent equipment not found"
            )
        # Prevent circular reference
        if update_data['parent_id'] == equipment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment cannot be its own parent"
            )
    
    for field, value in update_data.items():
        setattr(db_equipment, field, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


def delete_equipment(db: Session, equipment_id: int) -> bool:
    """Delete equipment."""
    db_equipment = get_equipment(db, equipment_id)
    if not db_equipment:
        return False
    
    # Check if equipment has children
    children = db.query(Equipment).filter(Equipment.parent_id == equipment_id).first()
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete equipment with child equipment"
        )
    
    db.delete(db_equipment)
    db.commit()
    return True


def get_equipment_children(db: Session, equipment_id: int) -> List[Equipment]:
    """Get child equipment."""
    return db.query(Equipment).filter(Equipment.parent_id == equipment_id).all()


def get_equipment_by_category(db: Session, category: str) -> List[Equipment]:
    """Get equipment by category."""
    return db.query(Equipment).filter(Equipment.category.ilike(f"%{category}%")).all()


def get_equipment_by_location(db: Session, location: str) -> List[Equipment]:
    """Get equipment by location."""
    return db.query(Equipment).filter(Equipment.location.ilike(f"%{location}%")).all()


def get_equipment_statistics(db: Session) -> dict:
    """Get equipment statistics."""
    total = db.query(Equipment).count()
    operational = db.query(Equipment).filter(Equipment.status == EquipmentStatus.OPERATIONAL).count()
    maintenance = db.query(Equipment).filter(Equipment.status == EquipmentStatus.MAINTENANCE).count()
    breakdown = db.query(Equipment).filter(Equipment.status == EquipmentStatus.BREAKDOWN).count()
    retired = db.query(Equipment).filter(Equipment.status == EquipmentStatus.RETIRED).count()
    
    return {
        "total": total,
        "operational": operational,
        "maintenance": maintenance,
        "breakdown": breakdown,
        "retired": retired
    }


# ==================== EQUIPMENT OPERATORS ====================

def get_equipment_operators(db: Session, equipment_id: int) -> List[dict]:
    """Get all operators (craftsmen) assigned to equipment."""
    equipment = get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    operators = []
    for craftsman in equipment.operators:
        operators.append({
            "craftsman_id": craftsman.id,
            "employee_id": craftsman.employee_id,
            "craftsman_name": craftsman.user.full_name if craftsman.user else "Unknown",
            "position": craftsman.position,
            "department": craftsman.department
        })
    
    return operators


def assign_operator(db: Session, equipment_id: int, craftsman_id: int) -> bool:
    """Assign a craftsman as an operator to equipment."""
    equipment = get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    craftsman = db.query(Craftsman).filter(Craftsman.id == craftsman_id).first()
    if not craftsman:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman not found"
        )
    
    # Check if already assigned
    if craftsman in equipment.operators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Craftsman is already assigned to this equipment"
        )
    
    equipment.operators.append(craftsman)
    db.commit()
    return True


def remove_operator(db: Session, equipment_id: int, craftsman_id: int) -> bool:
    """Remove a craftsman operator from equipment."""
    equipment = get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    craftsman = db.query(Craftsman).filter(Craftsman.id == craftsman_id).first()
    if not craftsman:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman not found"
        )
    
    # Check if assigned
    if craftsman not in equipment.operators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Craftsman is not assigned to this equipment"
        )
    
    equipment.operators.remove(craftsman)
    db.commit()
    return True
