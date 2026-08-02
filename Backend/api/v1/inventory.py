from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from models.inventory import TransactionType
from schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse, InventoryItemWithCategory,
    InventoryTransactionCreate, InventoryTransactionResponse,
    InventoryCategoryCreate, InventoryCategoryUpdate, InventoryCategoryResponse, InventoryCategoryTree
)
from schemas.common import PaginatedResponse
from services import inventory_service

router = APIRouter()


# ==================== CATEGORY ENDPOINTS ====================

@router.get("/categories", response_model=List[InventoryCategoryResponse])
async def list_categories(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all categories (flat list)."""
    return inventory_service.get_categories(db, include_inactive)


@router.get("/categories/tree", response_model=List[InventoryCategoryTree])
async def get_category_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get categories in tree structure."""
    return inventory_service.get_category_tree(db)


@router.post("/categories", response_model=InventoryCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: InventoryCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new category."""
    return inventory_service.create_category(db, category)


@router.get("/categories/{category_id}", response_model=InventoryCategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get category by ID."""
    category = inventory_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=InventoryCategoryResponse)
async def update_category(
    category_id: int,
    category: InventoryCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update category."""
    updated = inventory_service.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return updated


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete category (soft delete if has dependencies)."""
    deleted = inventory_service.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


# ==================== INVENTORY ITEM ENDPOINTS ====================

@router.get("/statistics")
async def get_inventory_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory statistics."""
    return inventory_service.get_inventory_statistics(db)


@router.get("/", response_model=PaginatedResponse[InventoryItemWithCategory])
async def list_inventory_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all inventory items with optional filters."""
    skip = (page - 1) * limit
    items = inventory_service.get_inventory_items(
        db, skip=skip, limit=limit, search=search,
        category_id=category_id, low_stock=low_stock
    )
    total = inventory_service.get_inventory_count(
        db, search=search, category_id=category_id, low_stock=low_stock
    )
    
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new inventory item."""
    return inventory_service.create_inventory_item(db, item)


@router.get("/low-stock", response_model=List[InventoryItemWithCategory])
async def get_low_stock_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get items below reorder point."""
    return inventory_service.get_low_stock_items(db)


@router.get("/{item_id}", response_model=InventoryItemWithCategory)
async def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory item by ID."""
    item = inventory_service.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update inventory item."""
    updated = inventory_service.update_inventory_item(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return updated


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete inventory item."""
    deleted = inventory_service.delete_inventory_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


@router.post("/{item_id}/adjust", response_model=InventoryItemResponse)
async def adjust_inventory(
    item_id: int,
    quantity: float = Body(..., embed=True),
    transaction_type: TransactionType = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True),
    reference: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Adjust inventory quantity."""
    return inventory_service.adjust_inventory_quantity(
        db, item_id, quantity, transaction_type,
        current_user.id, notes, reference
    )


@router.get("/{item_id}/transactions", response_model=List[InventoryTransactionResponse])
async def get_item_transactions(
    item_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get transaction history for an item."""
    item = inventory_service.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return inventory_service.get_item_transactions(db, item_id, skip, limit)


@router.get("/transactions/all", response_model=List[InventoryTransactionResponse])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all inventory transactions."""
    return inventory_service.get_transactions(db, skip, limit)
