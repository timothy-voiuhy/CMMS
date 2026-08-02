from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.work_order import WorkOrder, WorkOrderStatus, WorkOrderPriority, WorkOrderType
from schemas.work_order import WorkOrderCreate, WorkOrderUpdate


def generate_work_order_number(db: Session) -> str:
    """Generate unique work order number."""
    # Get count of work orders
    count = db.query(WorkOrder).count()
    return f"WO-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"


def get_work_order_statistics(db: Session) -> dict:
    """Get work order statistics."""
    total = db.query(func.count(WorkOrder.id)).scalar()
    
    pending = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.PENDING
    ).scalar()
    
    assigned = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.ASSIGNED
    ).scalar()
    
    in_progress = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.IN_PROGRESS
    ).scalar()
    
    completed = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.COMPLETED
    ).scalar()
    
    on_hold = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.ON_HOLD
    ).scalar()
    
    urgent = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.priority == WorkOrderPriority.URGENT
    ).scalar()
    
    return {
        "total": total,
        "pending": pending,
        "assigned": assigned,
        "in_progress": in_progress,
        "completed": completed,
        "on_hold": on_hold,
        "urgent": urgent
    }


def get_work_orders_count(db: Session, search: Optional[str] = None,
                         status_filter: Optional[WorkOrderStatus] = None,
                         priority: Optional[WorkOrderPriority] = None,
                         assigned_to: Optional[int] = None) -> int:
    """Get count of work orders with filters."""
    query = db.query(func.count(WorkOrder.id))
    
    if search:
        query = query.filter(
            or_(
                WorkOrder.work_order_number.ilike(f"%{search}%"),
                WorkOrder.title.ilike(f"%{search}%"),
                WorkOrder.description.ilike(f"%{search}%")
            )
        )
    
    if status_filter:
        query = query.filter(WorkOrder.status == status_filter)
    
    if priority:
        query = query.filter(WorkOrder.priority == priority)
    
    if assigned_to:
        query = query.filter(WorkOrder.assigned_to == assigned_to)
    
    return query.scalar()


def get_work_orders(db: Session, skip: int = 0, limit: int = 100,
                   search: Optional[str] = None,
                   status_filter: Optional[WorkOrderStatus] = None,
                   priority: Optional[WorkOrderPriority] = None,
                   assigned_to: Optional[int] = None) -> List[WorkOrder]:
    """Get all work orders with optional filters."""
    query = db.query(WorkOrder)
    
    if search:
        query = query.filter(
            or_(
                WorkOrder.work_order_number.ilike(f"%{search}%"),
                WorkOrder.title.ilike(f"%{search}%"),
                WorkOrder.description.ilike(f"%{search}%")
            )
        )
    
    if status_filter:
        query = query.filter(WorkOrder.status == status_filter)
    
    if priority:
        query = query.filter(WorkOrder.priority == priority)
    
    if assigned_to:
        query = query.filter(WorkOrder.assigned_to == assigned_to)
    
    return query.order_by(WorkOrder.created_at.desc()).offset(skip).limit(limit).all()


def get_work_order(db: Session, work_order_id: int) -> Optional[WorkOrder]:
    """Get work order by ID."""
    return db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()


def get_work_order_by_number(db: Session, work_order_number: str) -> Optional[WorkOrder]:
    """Get work order by number."""
    return db.query(WorkOrder).filter(WorkOrder.work_order_number == work_order_number).first()


def create_work_order(db: Session, work_order: WorkOrderCreate, created_by: int) -> WorkOrder:
    """Create new work order."""
    # Generate work order number
    wo_number = generate_work_order_number(db)
    
    db_work_order = WorkOrder(
        work_order_number=wo_number,
        created_by=created_by,
        **work_order.model_dump()
    )
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


def update_work_order(db: Session, work_order_id: int, work_order: WorkOrderUpdate) -> Optional[WorkOrder]:
    """Update work order."""
    db_work_order = get_work_order(db, work_order_id)
    if not db_work_order:
        return None
    
    update_data = work_order.model_dump(exclude_unset=True)
    
    # If status is being changed to IN_PROGRESS and started_at is None, set it
    if 'status' in update_data and update_data['status'] == WorkOrderStatus.IN_PROGRESS:
        if not db_work_order.started_at:
            update_data['started_at'] = datetime.now().isoformat()
    
    # If status is being changed to COMPLETED, set completed_at
    if 'status' in update_data and update_data['status'] == WorkOrderStatus.COMPLETED:
        if not db_work_order.completed_at:
            update_data['completed_at'] = datetime.now().isoformat()
    
    for field, value in update_data.items():
        setattr(db_work_order, field, value)
    
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


def delete_work_order(db: Session, work_order_id: int) -> bool:
    """Delete work order."""
    db_work_order = get_work_order(db, work_order_id)
    if not db_work_order:
        return False
    
    # Only allow deletion of pending or cancelled work orders
    if db_work_order.status not in [WorkOrderStatus.PENDING, WorkOrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending or cancelled work orders"
        )
    
    db.delete(db_work_order)
    db.commit()
    return True


def assign_work_order(db: Session, work_order_id: int, craftsman_id: int) -> Optional[WorkOrder]:
    """Assign work order to a craftsman."""
    db_work_order = get_work_order(db, work_order_id)
    if not db_work_order:
        return None
    
    db_work_order.assigned_to = craftsman_id
    if db_work_order.status == WorkOrderStatus.PENDING:
        db_work_order.status = WorkOrderStatus.ASSIGNED
    
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


def update_work_order_status(db: Session, work_order_id: int, 
                             new_status: WorkOrderStatus, 
                             notes: Optional[str] = None) -> Optional[WorkOrder]:
    """Update work order status."""
    db_work_order = get_work_order(db, work_order_id)
    if not db_work_order:
        return None
    
    db_work_order.status = new_status
    
    if new_status == WorkOrderStatus.IN_PROGRESS and not db_work_order.started_at:
        db_work_order.started_at = datetime.now().isoformat()
    
    if new_status == WorkOrderStatus.COMPLETED and not db_work_order.completed_at:
        db_work_order.completed_at = datetime.now().isoformat()
    
    if notes:
        if new_status == WorkOrderStatus.COMPLETED:
            db_work_order.completion_notes = notes
        else:
            db_work_order.notes = notes
    
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


def get_craftsman_work_orders(db: Session, craftsman_id: int) -> List[WorkOrder]:
    """Get work orders assigned to a craftsman."""
    return db.query(WorkOrder).filter(WorkOrder.assigned_to == craftsman_id).order_by(
        WorkOrder.created_at.desc()
    ).all()


def get_equipment_work_orders(db: Session, equipment_id: int) -> List[WorkOrder]:
    """Get work orders for an equipment."""
    return db.query(WorkOrder).filter(WorkOrder.equipment_id == equipment_id).order_by(
        WorkOrder.created_at.desc()
    ).all()
