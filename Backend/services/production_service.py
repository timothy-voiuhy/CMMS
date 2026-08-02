from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.production import (
    ProductionLine, ProductionLineEquipment, Shift, ProductionOrder, PackagingOrder,
    ProductionLineStatus, ProductionOrderStatus
)
from schemas.production import (
    ProductionLineCreate, ProductionLineUpdate,
    ProductionLineEquipmentCreate, ProductionLineEquipmentUpdate,
    ShiftCreate, ShiftUpdate,
    ProductionOrderCreate, ProductionOrderUpdate,
    PackagingOrderCreate, PackagingOrderUpdate
)


# Production Line Services
def generate_line_code(db: Session) -> str:
    """Generate unique production line code."""
    count = db.query(ProductionLine).count()
    return f"LINE-{count + 1:03d}"


def get_production_line_statistics(db: Session) -> dict:
    """Get production line statistics."""
    total = db.query(func.count(ProductionLine.id)).scalar()
    active = db.query(func.count(ProductionLine.id)).filter(
        ProductionLine.status == ProductionLineStatus.ACTIVE
    ).scalar()
    idle = db.query(func.count(ProductionLine.id)).filter(
        ProductionLine.status == ProductionLineStatus.IDLE
    ).scalar()
    maintenance = db.query(func.count(ProductionLine.id)).filter(
        ProductionLine.status == ProductionLineStatus.MAINTENANCE
    ).scalar()
    
    return {
        "total": total,
        "active": active,
        "idle": idle,
        "maintenance": maintenance
    }


def get_production_lines(db: Session, skip: int = 0, limit: int = 100,
                         search: Optional[str] = None,
                         status: Optional[ProductionLineStatus] = None) -> List[ProductionLine]:
    """Get all production lines with filters."""
    query = db.query(ProductionLine)
    
    if search:
        query = query.filter(
            or_(
                ProductionLine.line_code.ilike(f"%{search}%"),
                ProductionLine.name.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(ProductionLine.status == status)
    
    return query.order_by(ProductionLine.created_at.desc()).offset(skip).limit(limit).all()


def get_production_lines_count(db: Session, search: Optional[str] = None,
                               status: Optional[ProductionLineStatus] = None) -> int:
    """Get count of production lines."""
    query = db.query(func.count(ProductionLine.id))
    
    if search:
        query = query.filter(
            or_(
                ProductionLine.line_code.ilike(f"%{search}%"),
                ProductionLine.name.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(ProductionLine.status == status)
    
    return query.scalar()


def get_production_line(db: Session, line_id: int) -> Optional[ProductionLine]:
    """Get production line by ID."""
    return db.query(ProductionLine).filter(ProductionLine.id == line_id).first()


def create_production_line(db: Session, line: ProductionLineCreate) -> ProductionLine:
    """Create new production line."""
    db_line = ProductionLine(**line.model_dump())
    db.add(db_line)
    db.commit()
    db.refresh(db_line)
    return db_line


def update_production_line(db: Session, line_id: int, line: ProductionLineUpdate) -> Optional[ProductionLine]:
    """Update production line."""
    db_line = get_production_line(db, line_id)
    if not db_line:
        return None
    
    update_data = line.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_line, field, value)
    
    db.commit()
    db.refresh(db_line)
    return db_line


def delete_production_line(db: Session, line_id: int) -> bool:
    """Delete production line."""
    db_line = get_production_line(db, line_id)
    if not db_line:
        return False
    
    db.delete(db_line)
    db.commit()
    return True


# Shift Services
def get_shifts_by_line(db: Session, line_id: int) -> List[Shift]:
    """Get all shifts for a production line."""
    return db.query(Shift).filter(Shift.production_line_id == line_id).all()


def get_shift(db: Session, shift_id: int) -> Optional[Shift]:
    """Get shift by ID."""
    return db.query(Shift).filter(Shift.id == shift_id).first()


def create_shift(db: Session, shift: ShiftCreate) -> Shift:
    """Create new shift."""
    db_shift = Shift(**shift.model_dump())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift


def update_shift(db: Session, shift_id: int, shift: ShiftUpdate) -> Optional[Shift]:
    """Update shift."""
    db_shift = get_shift(db, shift_id)
    if not db_shift:
        return None
    
    update_data = shift.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_shift, field, value)
    
    db.commit()
    db.refresh(db_shift)
    return db_shift


def delete_shift(db: Session, shift_id: int) -> bool:
    """Delete shift."""
    db_shift = get_shift(db, shift_id)
    if not db_shift:
        return False
    
    db.delete(db_shift)
    db.commit()
    return True


# Production Order Services
def generate_production_order_number(db: Session) -> str:
    """Generate unique production order number."""
    count = db.query(ProductionOrder).count()
    return f"PO-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"


def get_production_order_statistics(db: Session) -> dict:
    """Get production order statistics."""
    total = db.query(func.count(ProductionOrder.id)).scalar()
    
    pending = db.query(func.count(ProductionOrder.id)).filter(
        ProductionOrder.status == ProductionOrderStatus.PENDING
    ).scalar()
    
    in_progress = db.query(func.count(ProductionOrder.id)).filter(
        ProductionOrder.status == ProductionOrderStatus.IN_PROGRESS
    ).scalar()
    
    completed = db.query(func.count(ProductionOrder.id)).filter(
        ProductionOrder.status == ProductionOrderStatus.COMPLETED
    ).scalar()
    
    paused = db.query(func.count(ProductionOrder.id)).filter(
        ProductionOrder.status == ProductionOrderStatus.PAUSED
    ).scalar()
    
    total_produced = db.query(
        func.sum(ProductionOrder.produced_quantity)
    ).scalar() or 0
    
    total_target = db.query(
        func.sum(ProductionOrder.target_quantity)
    ).scalar() or 0
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "paused": paused,
        "total_produced": float(total_produced),
        "total_target": float(total_target),
        "completion_rate": (total_produced / total_target * 100) if total_target > 0 else 0
    }


def get_production_orders(db: Session, skip: int = 0, limit: int = 100,
                         search: Optional[str] = None,
                         status: Optional[ProductionOrderStatus] = None,
                         line_id: Optional[int] = None) -> List[ProductionOrder]:
    """Get all production orders with filters."""
    query = db.query(ProductionOrder)
    
    if search:
        query = query.filter(
            or_(
                ProductionOrder.order_number.ilike(f"%{search}%"),
                ProductionOrder.product_name.ilike(f"%{search}%"),
                ProductionOrder.product_code.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(ProductionOrder.status == status)
    
    if line_id:
        query = query.filter(ProductionOrder.production_line_id == line_id)
    
    return query.order_by(ProductionOrder.created_at.desc()).offset(skip).limit(limit).all()


def get_production_orders_count(db: Session, search: Optional[str] = None,
                               status: Optional[ProductionOrderStatus] = None,
                               line_id: Optional[int] = None) -> int:
    """Get count of production orders."""
    query = db.query(func.count(ProductionOrder.id))
    
    if search:
        query = query.filter(
            or_(
                ProductionOrder.order_number.ilike(f"%{search}%"),
                ProductionOrder.product_name.ilike(f"%{search}%"),
                ProductionOrder.product_code.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(ProductionOrder.status == status)
    
    if line_id:
        query = query.filter(ProductionOrder.production_line_id == line_id)
    
    return query.scalar()


def get_production_order(db: Session, order_id: int) -> Optional[ProductionOrder]:
    """Get production order by ID."""
    return db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()


def create_production_order(db: Session, order: ProductionOrderCreate) -> ProductionOrder:
    """Create new production order."""
    order_number = generate_production_order_number(db)
    
    db_order = ProductionOrder(
        order_number=order_number,
        **order.model_dump()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_production_order(db: Session, order_id: int, order: ProductionOrderUpdate) -> Optional[ProductionOrder]:
    """Update production order."""
    db_order = get_production_order(db, order_id)
    if not db_order:
        return None
    
    update_data = order.model_dump(exclude_unset=True)
    
    # Auto-set timestamps based on status
    if 'status' in update_data:
        if update_data['status'] == ProductionOrderStatus.IN_PROGRESS and not db_order.actual_start:
            update_data['actual_start'] = datetime.now().isoformat()
        elif update_data['status'] == ProductionOrderStatus.COMPLETED and not db_order.actual_end:
            update_data['actual_end'] = datetime.now().isoformat()
    
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_production_order(db: Session, order_id: int) -> bool:
    """Delete production order."""
    db_order = get_production_order(db, order_id)
    if not db_order:
        return False
    
    db.delete(db_order)
    db.commit()
    return True


# Packaging Order Services
def generate_packaging_order_number(db: Session) -> str:
    """Generate unique packaging order number."""
    count = db.query(PackagingOrder).count()
    return f"PKG-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"


def get_packaging_order_statistics(db: Session) -> dict:
    """Get packaging order statistics."""
    total = db.query(func.count(PackagingOrder.id)).scalar()
    
    pending = db.query(func.count(PackagingOrder.id)).filter(
        PackagingOrder.status == ProductionOrderStatus.PENDING
    ).scalar()
    
    in_progress = db.query(func.count(PackagingOrder.id)).filter(
        PackagingOrder.status == ProductionOrderStatus.IN_PROGRESS
    ).scalar()
    
    completed = db.query(func.count(PackagingOrder.id)).filter(
        PackagingOrder.status == ProductionOrderStatus.COMPLETED
    ).scalar()
    
    total_packaged = db.query(
        func.sum(PackagingOrder.packaged_quantity)
    ).scalar() or 0
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "total_packaged": float(total_packaged)
    }


def get_packaging_orders(db: Session, skip: int = 0, limit: int = 100,
                        search: Optional[str] = None,
                        status: Optional[ProductionOrderStatus] = None) -> List[PackagingOrder]:
    """Get all packaging orders with filters."""
    query = db.query(PackagingOrder)
    
    if search:
        query = query.filter(
            or_(
                PackagingOrder.order_number.ilike(f"%{search}%"),
                PackagingOrder.product_name.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(PackagingOrder.status == status)
    
    return query.order_by(PackagingOrder.created_at.desc()).offset(skip).limit(limit).all()


def get_packaging_orders_count(db: Session, search: Optional[str] = None,
                               status: Optional[ProductionOrderStatus] = None) -> int:
    """Get count of packaging orders."""
    query = db.query(func.count(PackagingOrder.id))
    
    if search:
        query = query.filter(
            or_(
                PackagingOrder.order_number.ilike(f"%{search}%"),
                PackagingOrder.product_name.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(PackagingOrder.status == status)
    
    return query.scalar()


def get_packaging_order(db: Session, order_id: int) -> Optional[PackagingOrder]:
    """Get packaging order by ID."""
    return db.query(PackagingOrder).filter(PackagingOrder.id == order_id).first()


def create_packaging_order(db: Session, order: PackagingOrderCreate) -> PackagingOrder:
    """Create new packaging order."""
    order_number = generate_packaging_order_number(db)
    
    db_order = PackagingOrder(
        order_number=order_number,
        **order.model_dump()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_packaging_order(db: Session, order_id: int, order: PackagingOrderUpdate) -> Optional[PackagingOrder]:
    """Update packaging order."""
    db_order = get_packaging_order(db, order_id)
    if not db_order:
        return None
    
    update_data = order.model_dump(exclude_unset=True)
    
    # Auto-set timestamps based on status
    if 'status' in update_data:
        if update_data['status'] == ProductionOrderStatus.IN_PROGRESS and not db_order.actual_start:
            update_data['actual_start'] = datetime.now().isoformat()
        elif update_data['status'] == ProductionOrderStatus.COMPLETED and not db_order.actual_end:
            update_data['actual_end'] = datetime.now().isoformat()
    
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_packaging_order(db: Session, order_id: int) -> bool:
    """Delete packaging order."""
    db_order = get_packaging_order(db, order_id)
    if not db_order:
        return False
    
    db.delete(db_order)
    db.commit()
    return True


# Production Line Equipment Services
def get_line_equipment_stations(db: Session, line_id: int) -> List[ProductionLineEquipment]:
    """Get all equipment stations for a production line in sequence order."""
    return db.query(ProductionLineEquipment).filter(
        ProductionLineEquipment.production_line_id == line_id
    ).order_by(ProductionLineEquipment.sequence_order).all()


def get_line_equipment_station(db: Session, station_id: int) -> Optional[ProductionLineEquipment]:
    """Get a specific equipment station by ID."""
    return db.query(ProductionLineEquipment).filter(ProductionLineEquipment.id == station_id).first()


def create_line_equipment_station(db: Session, station: ProductionLineEquipmentCreate) -> ProductionLineEquipment:
    """Add equipment station to a production line."""
    db_station = ProductionLineEquipment(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


def update_line_equipment_station(db: Session, station_id: int, station: ProductionLineEquipmentUpdate) -> Optional[ProductionLineEquipment]:
    """Update equipment station configuration."""
    db_station = get_line_equipment_station(db, station_id)
    if not db_station:
        return None
    
    update_data = station.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_station, field, value)
    
    db.commit()
    db.refresh(db_station)
    return db_station


def delete_line_equipment_station(db: Session, station_id: int) -> bool:
    """Remove equipment station from production line."""
    db_station = get_line_equipment_station(db, station_id)
    if not db_station:
        return False
    
    db.delete(db_station)
    db.commit()
    return True


def reorder_line_equipment_stations(db: Session, line_id: int, station_orders: List[dict]) -> List[ProductionLineEquipment]:
    """
    Reorder equipment stations on a production line.
    station_orders should be a list of dicts like: [{"id": 1, "sequence_order": 1}, ...]
    """
    for order_data in station_orders:
        station = get_line_equipment_station(db, order_data['id'])
        if station and station.production_line_id == line_id:
            station.sequence_order = order_data['sequence_order']
    
    db.commit()
    return get_line_equipment_stations(db, line_id)
