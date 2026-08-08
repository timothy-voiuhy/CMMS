from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.inventory import InventoryItem
from models.maintenance import MaintenanceReport, MaintenanceCatalogueItem, MaintenanceCatalogueItemType
from models.work_order import WorkOrder
from models.equipment import Equipment
from models.craftsman import Craftsman
from schemas.maintenance import (
    MaintenanceReportCreate, MaintenanceReportUpdate,
    MaintenanceCatalogueItemCreate, MaintenanceCatalogueItemUpdate
)


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
    if not db.query(WorkOrder).filter(WorkOrder.id == report.work_order_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Work order {report.work_order_id} was not found. Select an existing work order."
        )
    if not db.query(Equipment).filter(Equipment.id == report.equipment_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Equipment {report.equipment_id} was not found."
        )
    if not db.query(Craftsman).filter(Craftsman.id == report.craftsman_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Craftsman {report.craftsman_id} was not found."
        )

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


# ==================== PARTS AND TOOLS CATALOGUE SERVICES ====================

def generate_catalogue_item_code(db: Session, item_type: MaintenanceCatalogueItemType) -> str:
    """Generate a unique catalogue item code."""
    prefix = "TL" if item_type == MaintenanceCatalogueItemType.TOOL else "SP"
    next_number = (db.query(func.count(MaintenanceCatalogueItem.id)).scalar() or 0) + 1
    while True:
        item_code = f"{prefix}-{next_number:04d}"
        if not db.query(MaintenanceCatalogueItem).filter(MaintenanceCatalogueItem.item_code == item_code).first():
            return item_code
        next_number += 1


def get_catalogue_items_count(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    item_type: Optional[MaintenanceCatalogueItemType] = None,
    include_inactive: bool = False
) -> int:
    """Get count of catalogue items with filters."""
    query = db.query(func.count(MaintenanceCatalogueItem.id))

    if search:
        query = query.filter(
            or_(
                MaintenanceCatalogueItem.item_code.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.name.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.description.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.manufacturer.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.model_number.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.supplier.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.compatible_equipment.ilike(f"%{search}%"),
            )
        )

    if category:
        query = query.filter(MaintenanceCatalogueItem.category == category)

    if item_type:
        query = query.filter(MaintenanceCatalogueItem.item_type == item_type.value)

    if not include_inactive:
        query = query.filter(MaintenanceCatalogueItem.is_active == True)

    return query.scalar()


def get_catalogue_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    item_type: Optional[MaintenanceCatalogueItemType] = None,
    include_inactive: bool = False
) -> List[MaintenanceCatalogueItem]:
    """Get catalogue items with optional filters."""
    query = db.query(MaintenanceCatalogueItem)

    if search:
        query = query.filter(
            or_(
                MaintenanceCatalogueItem.item_code.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.name.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.description.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.manufacturer.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.model_number.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.supplier.ilike(f"%{search}%"),
                MaintenanceCatalogueItem.compatible_equipment.ilike(f"%{search}%"),
            )
        )

    if category:
        query = query.filter(MaintenanceCatalogueItem.category == category)

    if item_type:
        query = query.filter(MaintenanceCatalogueItem.item_type == item_type.value)

    if not include_inactive:
        query = query.filter(MaintenanceCatalogueItem.is_active == True)

    return query.order_by(MaintenanceCatalogueItem.name).offset(skip).limit(limit).all()


def get_catalogue_item(db: Session, item_id: int) -> Optional[MaintenanceCatalogueItem]:
    """Get catalogue item by ID."""
    return db.query(MaintenanceCatalogueItem).filter(MaintenanceCatalogueItem.id == item_id).first()


def get_catalogue_item_by_code(db: Session, item_code: str) -> Optional[MaintenanceCatalogueItem]:
    """Get catalogue item by code."""
    return db.query(MaintenanceCatalogueItem).filter(MaintenanceCatalogueItem.item_code == item_code).first()


def get_catalogue_categories(db: Session) -> List[str]:
    """Get used catalogue categories."""
    rows = db.query(MaintenanceCatalogueItem.category).filter(
        MaintenanceCatalogueItem.category.isnot(None),
        MaintenanceCatalogueItem.category != ""
    ).distinct().order_by(MaintenanceCatalogueItem.category).all()
    return [row[0] for row in rows]


def _validate_inventory_item(db: Session, inventory_item_id: Optional[int]) -> None:
    if not inventory_item_id:
        return
    item = db.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Linked inventory item not found"
        )


def create_catalogue_item(db: Session, item: MaintenanceCatalogueItemCreate) -> MaintenanceCatalogueItem:
    """Create a maintenance catalogue item."""
    _validate_inventory_item(db, item.inventory_item_id)
    item_code = item.item_code or generate_catalogue_item_code(db, item.item_type)
    if get_catalogue_item_by_code(db, item_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalogue item code already exists"
        )

    item_data = item.model_dump()
    item_data["item_code"] = item_code
    item_data["item_type"] = item.item_type.value
    db_item = MaintenanceCatalogueItem(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_catalogue_item(
    db: Session,
    item_id: int,
    item: MaintenanceCatalogueItemUpdate
) -> Optional[MaintenanceCatalogueItem]:
    """Update a maintenance catalogue item."""
    db_item = get_catalogue_item(db, item_id)
    if not db_item:
        return None

    update_data = item.model_dump(exclude_unset=True)
    if "inventory_item_id" in update_data:
        _validate_inventory_item(db, update_data["inventory_item_id"])

    if "item_code" in update_data and update_data["item_code"]:
        existing = get_catalogue_item_by_code(db, update_data["item_code"])
        if existing and existing.id != item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Catalogue item code already exists"
            )

    if "item_type" in update_data and update_data["item_type"]:
        update_data["item_type"] = update_data["item_type"].value

    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


def delete_catalogue_item(db: Session, item_id: int) -> bool:
    """Deactivate a maintenance catalogue item."""
    db_item = get_catalogue_item(db, item_id)
    if not db_item:
        return False

    db_item.is_active = False
    db.commit()
    return True
