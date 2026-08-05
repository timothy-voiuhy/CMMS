from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.inventory import (
    InventoryItem, InventoryTransaction, InventoryCategory, TransactionType,
    InventoryRequisition, InventoryRequisitionItem, RequisitionStatus,
    RequisitionLineStatus, RequisitionPriority
)
from schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryTransactionCreate,
    InventoryCategoryCreate, InventoryCategoryUpdate,
    InventoryRequisitionCreate, InventoryRequisitionUpdate,
    InventoryRequisitionApprovalRequest, InventoryRequisitionRejectRequest,
    InventoryRequisitionFulfillmentRequest
)


# ==================== CATEGORY SERVICES ====================

def get_categories(db: Session, include_inactive: bool = False) -> List[InventoryCategory]:
    """Get all categories (flat list)."""
    query = db.query(InventoryCategory)
    if not include_inactive:
        query = query.filter(InventoryCategory.is_active == True)
    return query.order_by(InventoryCategory.name).all()


def get_category_tree(db: Session) -> List[InventoryCategory]:
    """Get categories in tree structure (root categories with children)."""
    # Get all active categories
    categories = db.query(InventoryCategory).filter(
        InventoryCategory.is_active == True
    ).all()
    
    # Build tree structure (only root level, children will be included via relationship)
    root_categories = [cat for cat in categories if cat.parent_id is None]
    return root_categories


def get_category(db: Session, category_id: int) -> Optional[InventoryCategory]:
    """Get category by ID."""
    return db.query(InventoryCategory).filter(
        InventoryCategory.id == category_id
    ).first()


def create_category(db: Session, category: InventoryCategoryCreate) -> InventoryCategory:
    """Create new category."""
    # Validate parent exists if provided
    if category.parent_id:
        parent = get_category(db, category.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
    
    db_category = InventoryCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: InventoryCategoryUpdate) -> Optional[InventoryCategory]:
    """Update category."""
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    # Validate parent exists if provided
    update_data = category.model_dump(exclude_unset=True)
    if 'parent_id' in update_data and update_data['parent_id']:
        if update_data['parent_id'] == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent"
            )
        parent = get_category(db, update_data['parent_id'])
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete category (soft delete by setting is_active=False if has items)."""
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    # Check if category has items
    item_count = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.category_id == category_id
    ).scalar()
    
    # Check if category has children
    children_count = db.query(func.count(InventoryCategory.id)).filter(
        InventoryCategory.parent_id == category_id
    ).scalar()
    
    if item_count > 0 or children_count > 0:
        # Soft delete
        db_category.is_active = False
        db.commit()
    else:
        # Hard delete if no dependencies
        db.delete(db_category)
        db.commit()
    
    return True


# ==================== INVENTORY SERVICES ====================

def get_inventory_statistics(db: Session) -> dict:
    """Get inventory statistics."""
    total_items = db.query(func.count(InventoryItem.id)).scalar()
    
    low_stock_count = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.quantity <= InventoryItem.reorder_point
    ).scalar()
    
    out_of_stock_count = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.quantity <= 0
    ).scalar()
    
    total_value = db.query(
        func.sum(InventoryItem.quantity * InventoryItem.unit_cost)
    ).scalar() or 0
    
    # Get category counts (using actual category names)
    category_counts = {}
    categories = db.query(InventoryCategory).filter(InventoryCategory.is_active == True).all()
    for category in categories:
        count = db.query(func.count(InventoryItem.id)).filter(
            InventoryItem.category_id == category.id
        ).scalar()
        category_counts[category.name] = count
    
    return {
        "total_items": total_items,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "total_value": round(total_value, 2),
        "category_counts": category_counts
    }


def get_inventory_count(db: Session, search: Optional[str] = None,
                       category_id: Optional[int] = None,
                       low_stock: bool = False) -> int:
    """Get count of inventory items with filters."""
    query = db.query(func.count(InventoryItem.id))
    
    if search:
        query = query.filter(
            or_(
                InventoryItem.name.ilike(f"%{search}%"),
                InventoryItem.item_code.ilike(f"%{search}%"),
                InventoryItem.description.ilike(f"%{search}%")
            )
        )
    
    if category_id:
        query = query.filter(InventoryItem.category_id == category_id)
    
    if low_stock:
        query = query.filter(InventoryItem.quantity <= InventoryItem.reorder_point)
    
    return query.scalar()


def get_inventory_items(db: Session, skip: int = 0, limit: int = 100,
                        search: Optional[str] = None,
                        category_id: Optional[int] = None,
                        low_stock: bool = False) -> List[InventoryItem]:
    """Get all inventory items with optional filters."""
    query = db.query(InventoryItem).options(joinedload(InventoryItem.category))
    
    if search:
        query = query.filter(
            or_(
                InventoryItem.name.ilike(f"%{search}%"),
                InventoryItem.item_code.ilike(f"%{search}%"),
                InventoryItem.description.ilike(f"%{search}%")
            )
        )
    
    if category_id:
        query = query.filter(InventoryItem.category_id == category_id)
    
    if low_stock:
        query = query.filter(InventoryItem.quantity <= InventoryItem.reorder_point)
    
    return query.offset(skip).limit(limit).all()


def get_inventory_item(db: Session, item_id: int) -> Optional[InventoryItem]:
    """Get inventory item by ID."""
    return db.query(InventoryItem).options(
        joinedload(InventoryItem.category)
    ).filter(InventoryItem.id == item_id).first()


def get_inventory_item_by_code(db: Session, item_code: str) -> Optional[InventoryItem]:
    """Get inventory item by code."""
    return db.query(InventoryItem).filter(InventoryItem.item_code == item_code).first()


def create_inventory_item(db: Session, item: InventoryItemCreate) -> InventoryItem:
    """Create new inventory item."""
    # Check if item_code is unique
    existing = get_inventory_item_by_code(db, item.item_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item code already exists"
        )
    
    db_item = InventoryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_inventory_item(db: Session, item_id: int, item: InventoryItemUpdate) -> Optional[InventoryItem]:
    """Update inventory item."""
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        return None
    
    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_inventory_item(db: Session, item_id: int) -> bool:
    """Delete inventory item."""
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True


def adjust_inventory_quantity(db: Session, item_id: int, quantity_change: float, 
                              transaction_type: TransactionType, user_id: int,
                              notes: Optional[str] = None, reference: Optional[str] = None) -> InventoryItem:
    """Adjust inventory quantity and create transaction."""
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Calculate new quantity
    if transaction_type in [TransactionType.RECEIPT, TransactionType.RETURN]:
        new_quantity = db_item.quantity + abs(quantity_change)
    elif transaction_type in [TransactionType.ISSUE, TransactionType.SCRAP, TransactionType.ADJUSTMENT]:
        new_quantity = db_item.quantity - abs(quantity_change)
    else:  # TRANSFER
        new_quantity = db_item.quantity + quantity_change  # Can be positive or negative
    
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient quantity"
        )
    
    # Update quantity
    db_item.quantity = new_quantity
    
    # Create transaction record
    transaction = InventoryTransaction(
        item_id=item_id,
        transaction_type=transaction_type,
        quantity=quantity_change,
        unit_cost=db_item.unit_cost,
        reference_number=reference,
        notes=notes,
        performed_by=user_id
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item_transactions(db: Session, item_id: int, skip: int = 0, limit: int = 100) -> List[InventoryTransaction]:
    """Get transaction history for an item."""
    return db.query(InventoryTransaction).filter(
        InventoryTransaction.item_id == item_id
    ).order_by(InventoryTransaction.created_at.desc()).offset(skip).limit(limit).all()


def get_low_stock_items(db: Session) -> List[InventoryItem]:
    """Get items below reorder point."""
    return db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.reorder_point
    ).all()


def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[InventoryTransaction]:
    """Get all transactions."""
    return db.query(InventoryTransaction).order_by(
        InventoryTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()


# ==================== REQUISITION SERVICES ====================

def generate_requisition_number(db: Session) -> str:
    """Generate a human-readable requisition number."""
    prefix = f"REQ-{datetime.utcnow().strftime('%Y%m')}"
    count = db.query(func.count(InventoryRequisition.id)).filter(
        InventoryRequisition.requisition_number.ilike(f"{prefix}-%")
    ).scalar()
    return f"{prefix}-{(count or 0) + 1:04d}"


def _get_requisition_query(db: Session):
    return db.query(InventoryRequisition).options(
        joinedload(InventoryRequisition.items).joinedload(InventoryRequisitionItem.item)
    )


def get_requisition(db: Session, requisition_id: int) -> Optional[InventoryRequisition]:
    """Get requisition by ID."""
    return _get_requisition_query(db).filter(
        InventoryRequisition.id == requisition_id
    ).first()


def get_requisition_count(
    db: Session,
    search: Optional[str] = None,
    status_filter: Optional[RequisitionStatus] = None,
    priority: Optional[RequisitionPriority] = None,
    requested_by: Optional[int] = None,
    work_order_id: Optional[int] = None,
    production_order_id: Optional[int] = None
) -> int:
    """Get count of requisitions with filters."""
    query = db.query(func.count(InventoryRequisition.id))

    if search:
        query = query.filter(
            or_(
                InventoryRequisition.requisition_number.ilike(f"%{search}%"),
                InventoryRequisition.title.ilike(f"%{search}%"),
                InventoryRequisition.description.ilike(f"%{search}%"),
                InventoryRequisition.department.ilike(f"%{search}%")
            )
        )

    if status_filter:
        query = query.filter(InventoryRequisition.status == status_filter)
    if priority:
        query = query.filter(InventoryRequisition.priority == priority)
    if requested_by:
        query = query.filter(InventoryRequisition.requested_by == requested_by)
    if work_order_id:
        query = query.filter(InventoryRequisition.work_order_id == work_order_id)
    if production_order_id:
        query = query.filter(InventoryRequisition.production_order_id == production_order_id)

    return query.scalar()


def get_requisitions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status_filter: Optional[RequisitionStatus] = None,
    priority: Optional[RequisitionPriority] = None,
    requested_by: Optional[int] = None,
    work_order_id: Optional[int] = None,
    production_order_id: Optional[int] = None
) -> List[InventoryRequisition]:
    """Get requisitions with optional filters."""
    query = _get_requisition_query(db)

    if search:
        query = query.filter(
            or_(
                InventoryRequisition.requisition_number.ilike(f"%{search}%"),
                InventoryRequisition.title.ilike(f"%{search}%"),
                InventoryRequisition.description.ilike(f"%{search}%"),
                InventoryRequisition.department.ilike(f"%{search}%")
            )
        )

    if status_filter:
        query = query.filter(InventoryRequisition.status == status_filter)
    if priority:
        query = query.filter(InventoryRequisition.priority == priority)
    if requested_by:
        query = query.filter(InventoryRequisition.requested_by == requested_by)
    if work_order_id:
        query = query.filter(InventoryRequisition.work_order_id == work_order_id)
    if production_order_id:
        query = query.filter(InventoryRequisition.production_order_id == production_order_id)

    return query.order_by(InventoryRequisition.created_at.desc()).offset(skip).limit(limit).all()


def _validate_requisition_items(db: Session, items: List) -> List[tuple]:
    validated_items = []
    seen_item_ids = set()

    for line in items:
        if line.item_id in seen_item_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate items are not allowed in the same requisition"
            )
        seen_item_ids.add(line.item_id)

        item = get_inventory_item(db, line.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Inventory item {line.item_id} not found"
            )
        validated_items.append((line, item))

    return validated_items


def _replace_requisition_items(db: Session, requisition: InventoryRequisition, items: List) -> None:
    validated_items = _validate_requisition_items(db, items)
    requisition.items.clear()
    db.flush()

    for line, item in validated_items:
        requisition.items.append(InventoryRequisitionItem(
            item_id=item.id,
            requested_quantity=line.requested_quantity,
            unit_of_measure=item.unit_of_measure,
            notes=line.notes,
            status=RequisitionLineStatus.PENDING
        ))


def create_requisition(
    db: Session,
    requisition: InventoryRequisitionCreate,
    requested_by: int
) -> InventoryRequisition:
    """Create a draft inventory requisition."""
    db_requisition = InventoryRequisition(
        requisition_number=generate_requisition_number(db),
        title=requisition.title,
        description=requisition.description,
        priority=requisition.priority,
        needed_by=requisition.needed_by,
        department=requisition.department,
        work_order_id=requisition.work_order_id,
        production_order_id=requisition.production_order_id,
        notes=requisition.notes,
        requested_by=requested_by,
        status=RequisitionStatus.DRAFT
    )
    db.add(db_requisition)
    _replace_requisition_items(db, db_requisition, requisition.items)
    db.commit()
    db.refresh(db_requisition)
    return get_requisition(db, db_requisition.id)


def update_requisition(
    db: Session,
    requisition_id: int,
    requisition: InventoryRequisitionUpdate
) -> Optional[InventoryRequisition]:
    """Update a draft requisition."""
    db_requisition = get_requisition(db, requisition_id)
    if not db_requisition:
        return None
    if db_requisition.status != RequisitionStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft requisitions can be edited"
        )

    update_data = requisition.model_dump(exclude_unset=True, exclude={"items"})
    for field, value in update_data.items():
        setattr(db_requisition, field, value)

    if requisition.items is not None:
        if len(requisition.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A requisition must include at least one item"
            )
        _replace_requisition_items(db, db_requisition, requisition.items)

    db.commit()
    db.refresh(db_requisition)
    return get_requisition(db, db_requisition.id)


def submit_requisition(db: Session, requisition_id: int) -> Optional[InventoryRequisition]:
    """Submit a draft requisition for approval."""
    db_requisition = get_requisition(db, requisition_id)
    if not db_requisition:
        return None
    if db_requisition.status != RequisitionStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft requisitions can be submitted"
        )
    if not db_requisition.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A requisition must include at least one item"
        )

    db_requisition.status = RequisitionStatus.SUBMITTED
    db.commit()
    db.refresh(db_requisition)
    return get_requisition(db, db_requisition.id)


def approve_requisition(
    db: Session,
    requisition_id: int,
    approval: InventoryRequisitionApprovalRequest,
    approved_by: int
) -> Optional[InventoryRequisition]:
    """Approve a submitted requisition."""
    db_requisition = get_requisition(db, requisition_id)
    if not db_requisition:
        return None
    if db_requisition.status != RequisitionStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted requisitions can be approved"
        )

    approval_by_line = {line.line_id: line.approved_quantity for line in approval.items or []}
    known_line_ids = {line.id for line in db_requisition.items}
    unknown_line_ids = set(approval_by_line) - known_line_ids
    if unknown_line_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval includes unknown requisition lines"
        )

    has_approved_quantity = False
    for line in db_requisition.items:
        approved_quantity = approval_by_line.get(line.id, line.requested_quantity)
        if approved_quantity > line.requested_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approved quantity cannot exceed requested quantity"
            )
        line.approved_quantity = approved_quantity
        line.status = RequisitionLineStatus.APPROVED if approved_quantity > 0 else RequisitionLineStatus.REJECTED
        has_approved_quantity = has_approved_quantity or approved_quantity > 0

    if not has_approved_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one line must have an approved quantity"
        )

    db_requisition.status = RequisitionStatus.APPROVED
    db_requisition.approved_by = approved_by
    db_requisition.approved_at = datetime.utcnow()
    if approval.notes:
        db_requisition.notes = approval.notes

    db.commit()
    db.refresh(db_requisition)
    return get_requisition(db, db_requisition.id)


def reject_requisition(
    db: Session,
    requisition_id: int,
    rejection: InventoryRequisitionRejectRequest,
    rejected_by: int
) -> Optional[InventoryRequisition]:
    """Reject a submitted requisition."""
    db_requisition = get_requisition(db, requisition_id)
    if not db_requisition:
        return None
    if db_requisition.status != RequisitionStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted requisitions can be rejected"
        )

    db_requisition.status = RequisitionStatus.REJECTED
    db_requisition.approved_by = rejected_by
    db_requisition.approved_at = datetime.utcnow()
    db_requisition.rejection_reason = rejection.reason
    for line in db_requisition.items:
        line.status = RequisitionLineStatus.REJECTED
        line.approved_quantity = 0

    db.commit()
    db.refresh(db_requisition)
    return get_requisition(db, db_requisition.id)


def fulfill_requisition(
    db: Session,
    requisition_id: int,
    fulfillment: InventoryRequisitionFulfillmentRequest,
    fulfilled_by: int
) -> Optional[InventoryRequisition]:
    """Issue stock against an approved requisition."""
    db_requisition = get_requisition(db, requisition_id)
    if not db_requisition:
        return None
    if db_requisition.status not in [RequisitionStatus.APPROVED, RequisitionStatus.PARTIALLY_FULFILLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved requisitions can be fulfilled"
        )

    lines_by_id = {line.id: line for line in db_requisition.items}
    for fulfillment_line in fulfillment.items:
        line = lines_by_id.get(fulfillment_line.line_id)
        if not line:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fulfillment includes unknown requisition lines"
            )
        approved_quantity = line.approved_quantity if line.approved_quantity is not None else line.requested_quantity
        remaining_quantity = approved_quantity - line.fulfilled_quantity
        if fulfillment_line.quantity > remaining_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fulfillment quantity exceeds remaining approved quantity for line {line.id}"
            )
        if line.item.quantity < fulfillment_line.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {line.item.name}"
            )

    for fulfillment_line in fulfillment.items:
        line = lines_by_id[fulfillment_line.line_id]
        line.item.quantity -= fulfillment_line.quantity
        line.fulfilled_quantity += fulfillment_line.quantity
        approved_quantity = line.approved_quantity if line.approved_quantity is not None else line.requested_quantity

        if line.fulfilled_quantity >= approved_quantity:
            line.status = RequisitionLineStatus.FULFILLED
        else:
            line.status = RequisitionLineStatus.PARTIALLY_FULFILLED

        db.add(InventoryTransaction(
            item_id=line.item_id,
            transaction_type=TransactionType.ISSUE,
            quantity=-abs(fulfillment_line.quantity),
            unit_cost=line.item.unit_cost,
            reference_number=db_requisition.requisition_number,
            notes=fulfillment.notes or f"Issued for requisition {db_requisition.requisition_number}",
            performed_by=fulfilled_by
        ))

    active_lines = [line for line in db_requisition.items if (line.approved_quantity or 0) > 0]
    if active_lines and all(line.status == RequisitionLineStatus.FULFILLED for line in active_lines):
        db_requisition.status = RequisitionStatus.FULFILLED
        db_requisition.fulfilled_at = datetime.utcnow()
    else:
        db_requisition.status = RequisitionStatus.PARTIALLY_FULFILLED

    db_requisition.fulfilled_by = fulfilled_by
    db.commit()
    db.refresh(db_requisition)
    return get_requisition(db, db_requisition.id)


def cancel_requisition(
    db: Session,
    requisition_id: int
) -> Optional[InventoryRequisition]:
    """Cancel a requisition before any fulfillment has happened."""
    db_requisition = get_requisition(db, requisition_id)
    if not db_requisition:
        return None
    if db_requisition.status in [
        RequisitionStatus.REJECTED,
        RequisitionStatus.FULFILLED,
        RequisitionStatus.CANCELLED
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This requisition cannot be cancelled"
        )
    if any(line.fulfilled_quantity > 0 for line in db_requisition.items):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a requisition after fulfillment has started"
        )

    db_requisition.status = RequisitionStatus.CANCELLED
    for line in db_requisition.items:
        line.status = RequisitionLineStatus.CANCELLED

    db.commit()
    db.refresh(db_requisition)
    return get_requisition(db, db_requisition.id)
