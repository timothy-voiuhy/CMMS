from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.inventory import InventoryItem, InventoryTransaction, InventoryCategory, TransactionType
from schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryTransactionCreate,
    InventoryCategoryCreate, InventoryCategoryUpdate
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
