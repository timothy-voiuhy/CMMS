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
    craftsman = db.query(Craftsman).filter(Craftsman.id == craftsman_id).first()
    if not craftsman:
        return []
    
    equipment_list = []
    for equipment in craftsman.operated_equipment:
        status_val = equipment.status.value if hasattr(equipment.status, 'value') else str(equipment.status)
        equipment_list.append({
            "id": equipment.id,
            "name": equipment.name,
            "equipment_id": equipment.equipment_id,
            "category": equipment.category,
            "status": status_val
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
        priority_val = wo.priority.value if hasattr(wo.priority, 'value') else str(wo.priority)
        status_val = wo.status.value if hasattr(wo.status, 'value') else str(wo.status)
        created_at_str = wo.created_at.isoformat() if hasattr(wo.created_at, 'isoformat') else str(wo.created_at or "")
        due_date_str = wo.due_date.isoformat() if hasattr(wo.due_date, 'isoformat') else (str(wo.due_date) if wo.due_date else None)
        
        result.append({
            "id": wo.id,
            "work_order_number": wo.work_order_number,
            "title": wo.title,
            "priority": priority_val,
            "status": status_val,
            "created_at": created_at_str,
            "due_date": due_date_str
        })
    
    return result



def get_distinct_departments(db: Session) -> List[str]:
    """Get list of unique departments from craftsmen."""
    departments = db.query(Craftsman.department)\
        .filter(Craftsman.department.isnot(None))\
        .filter(Craftsman.department != '')\
        .distinct()\
        .order_by(Craftsman.department)\
        .all()
    return [dept[0] for dept in departments if dept[0]]


def get_distinct_positions(db: Session) -> List[str]:
    """Get list of unique positions from craftsmen."""
    positions = db.query(Craftsman.position)\
        .filter(Craftsman.position.isnot(None))\
        .filter(Craftsman.position != '')\
        .distinct()\
        .order_by(Craftsman.position)\
        .all()
    return [pos[0] for pos in positions if pos[0]]



def create_craftsman_with_user(
    db: Session,
    full_name: str,
    username: str,
    email: str,
    password: str,
    phone: Optional[str],
    employee_id: str,
    department: Optional[str],
    position: Optional[str],
    role_id: Optional[int],
    hire_date: Optional[str],
    certification_level: Optional[str],
    hourly_rate: Optional[float],
    notes: Optional[str]
) -> Craftsman:
    """Create a new user and craftsman profile together."""
    from core.security import get_password_hash
    from models.user import UserRole
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    # Check if employee_id is unique
    existing_emp = db.query(Craftsman).filter(Craftsman.employee_id == employee_id).first()
    if existing_emp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee ID already exists")
    
    # Create user
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        phone=phone,
        role=UserRole.CRAFTSMAN,
        is_active=True
    )
    db.add(db_user)
    db.flush()  # Get the user ID without committing
    
    # Create craftsman
    db_craftsman = Craftsman(
        user_id=db_user.id,
        employee_id=employee_id,
        department=department,
        position=position,
        role_id=role_id,
        hire_date=hire_date,
        certification_level=certification_level,
        hourly_rate=hourly_rate,
        notes=notes
    )
    db.add(db_craftsman)
    db.commit()
    db.refresh(db_craftsman)
    return db_craftsman
