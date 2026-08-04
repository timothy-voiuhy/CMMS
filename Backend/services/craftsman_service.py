from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.craftsman import Craftsman, Skill
from models.user import User
from schemas.craftsman import CraftsmanCreate, CraftsmanUpdate


def get_craftsmen(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Craftsman]:
    """Get all craftsmen with optional search."""
    query = db.query(Craftsman).join(User)
    
    if search:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                Craftsman.employee_id.ilike(f"%{search}%"),
                Craftsman.department.ilike(f"%{search}%")
            )
        )
    
    return query.offset(skip).limit(limit).all()


def get_craftsmen_count(db: Session, search: Optional[str] = None) -> int:
    """Get total count of craftsmen with optional search."""
    query = db.query(Craftsman).join(User)
    
    if search:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                Craftsman.employee_id.ilike(f"%{search}%"),
                Craftsman.department.ilike(f"%{search}%")
            )
        )
    
    return query.count()


def get_craftsman_statistics(db: Session) -> dict:
    """Get craftsman statistics."""
    total = db.query(Craftsman).count()
    active = db.query(Craftsman).join(User).filter(User.is_active == True).count()
    inactive = total - active
    
    # Get count by department
    departments = db.query(Craftsman.department, func.count(Craftsman.id)).group_by(Craftsman.department).all()
    by_department = {dept: count for dept, count in departments if dept}
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "byDepartment": by_department
    }


def get_craftsman(db: Session, craftsman_id: int) -> Optional[Craftsman]:
    """Get a craftsman by ID."""
    return db.query(Craftsman).filter(Craftsman.id == craftsman_id).first()


def get_craftsman_by_user_id(db: Session, user_id: int) -> Optional[Craftsman]:
    """Get a craftsman by user ID."""
    return db.query(Craftsman).filter(Craftsman.user_id == user_id).first()


def create_craftsman(db: Session, craftsman: CraftsmanCreate) -> Craftsman:
    """Create a new craftsman."""
    # Check if user exists
    user = db.query(User).filter(User.id == craftsman.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if user already has a craftsman profile
    existing = db.query(Craftsman).filter(Craftsman.user_id == craftsman.user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has a craftsman profile")
    
    # Check if employee_id is unique
    existing_emp = db.query(Craftsman).filter(Craftsman.employee_id == craftsman.employee_id).first()
    if existing_emp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee ID already exists")
    
    db_craftsman = Craftsman(**craftsman.model_dump())
    db.add(db_craftsman)
    db.commit()
    db.refresh(db_craftsman)
    return db_craftsman


def update_craftsman(db: Session, craftsman_id: int, craftsman: CraftsmanUpdate) -> Optional[Craftsman]:
    """Update a craftsman."""
    db_craftsman = get_craftsman(db, craftsman_id)
    if not db_craftsman:
        return None
    
    update_data = craftsman.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_craftsman, field, value)
    
    db.commit()
    db.refresh(db_craftsman)
    return db_craftsman


def delete_craftsman(db: Session, craftsman_id: int) -> bool:
    """Delete a craftsman."""
    db_craftsman = get_craftsman(db, craftsman_id)
    if not db_craftsman:
        return False
    
    db.delete(db_craftsman)
    db.commit()
    return True


def add_skill_to_craftsman(db: Session, craftsman_id: int, skill_id: int) -> Optional[Craftsman]:
    """Add a skill to a craftsman."""
    craftsman = get_craftsman(db, craftsman_id)
    if not craftsman:
        return None
    
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    if skill not in craftsman.skills:
        craftsman.skills.append(skill)
        db.commit()
        db.refresh(craftsman)
    
    return craftsman


def remove_skill_from_craftsman(db: Session, craftsman_id: int, skill_id: int) -> Optional[Craftsman]:
    """Remove a skill from a craftsman."""
    craftsman = get_craftsman(db, craftsman_id)
    if not craftsman:
        return None
    
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if skill and skill in craftsman.skills:
        craftsman.skills.remove(skill)
        db.commit()
        db.refresh(craftsman)
    
    return craftsman


# Skills management
def get_skills(db: Session, skip: int = 0, limit: int = 100) -> List[Skill]:
    """Get all skills."""
    return db.query(Skill).offset(skip).limit(limit).all()


def get_skill(db: Session, skill_id: int) -> Optional[Skill]:
    """Get a skill by ID."""
    return db.query(Skill).filter(Skill.id == skill_id).first()


def create_skill(db: Session, name: str, description: Optional[str] = None, category: Optional[str] = None) -> Skill:
    """Create a new skill."""
    existing = db.query(Skill).filter(Skill.name == name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Skill already exists")
    
    skill = Skill(name=name, description=description, category=category)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def get_individual_craftsman_statistics(db: Session, craftsman_id: int) -> dict:
    """Get statistics for an individual craftsman."""
    from models.work_order import WorkOrder, WorkOrderStatus
    
    # Get work order counts
    total_work_orders = db.query(WorkOrder).filter(WorkOrder.assigned_to == craftsman_id).count()
    completed = db.query(WorkOrder).filter(
        WorkOrder.assigned_to == craftsman_id,
        WorkOrder.status == WorkOrderStatus.COMPLETED
    ).count()
    pending = db.query(WorkOrder).filter(
        WorkOrder.assigned_to == craftsman_id,
        WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.IN_PROGRESS])
    ).count()
    
    # Calculate average completion time (placeholder for now)
    average_completion_time = 0  # TODO: Calculate from actual completion times
    
    return {
        "totalWorkOrders": total_work_orders,
        "completedWorkOrders": completed,
        "pendingWorkOrders": pending,
        "averageCompletionTime": average_completion_time
    }


def get_craftsman_equipment(db: Session, craftsman_id: int) -> List:
    """Get equipment operated by a craftsman."""
    from models.equipment import Equipment, EquipmentOperator
    
    operators = db.query(EquipmentOperator).filter(
        EquipmentOperator.craftsman_id == craftsman_id
    ).all()
    
    equipment_list = []
    for op in operators:
        equipment = db.query(Equipment).filter(Equipment.id == op.equipment_id).first()
        if equipment:
            equipment_list.append({
                "id": equipment.id,
                "name": equipment.name,
                "equipment_id": equipment.equipment_id,
                "category": equipment.category,
                "status": equipment.status.value
            })
    
    return equipment_list


def get_craftsman_work_orders(db: Session, craftsman_id: int) -> List:
    """Get work orders assigned to a craftsman."""
    from models.work_order import WorkOrder
    
    work_orders = db.query(WorkOrder).filter(
        WorkOrder.assigned_to == craftsman_id
    ).all()
    
    result = []
    for wo in work_orders:
        result.append({
            "id": wo.id,
            "work_order_number": wo.work_order_number,
            "title": wo.title,
            "priority": wo.priority.value,
            "status": wo.status.value,
            "created_at": wo.created_at.isoformat(),
            "due_date": wo.due_date.isoformat() if wo.due_date else None
        })
    
    return result
