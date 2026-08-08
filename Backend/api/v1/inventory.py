from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from models.inventory import TransactionType, RequisitionStatus, RequisitionPriority
from schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse, InventoryItemWithCategory,
    InventoryTransactionCreate, InventoryTransactionResponse,
    InventoryCategoryCreate, InventoryCategoryUpdate, InventoryCategoryResponse, InventoryCategoryTree,
    InventoryRequisitionCreate, InventoryRequisitionUpdate, InventoryRequisitionResponse,
    InventoryRequisitionListResponse, InventoryRequisitionApprovalRequest,
    InventoryRequisitionRejectRequest, InventoryRequisitionFulfillmentRequest,
    InventoryRequisitionApproverAssignmentRequest, InventoryRequisitionApproverResponse
)
from schemas.common import PaginatedResponse
from services import inventory_service
from services.company_service import get_user_permissions

router = APIRouter()


def require_any_permission(db: Session, current_user: User, permissions: List[str]) -> None:
    """Require any matching resolved permission for sensitive inventory actions."""
    user_permissions = set(get_user_permissions(db, current_user.id))
    if (
        "*" in user_permissions
        or "admin.full_access" in user_permissions
        or any(permission in user_permissions for permission in permissions)
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )


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


# ==================== REQUISITION ENDPOINTS ====================

@router.get("/requisitions", response_model=PaginatedResponse[InventoryRequisitionListResponse])
async def list_requisitions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[RequisitionStatus] = Query(None, alias="status"),
    priority: Optional[RequisitionPriority] = None,
    requested_by: Optional[int] = None,
    work_order_id: Optional[int] = None,
    production_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all inventory requisitions with optional filters."""
    require_any_permission(db, current_user, ["inventory.requisitions.view", "inventory.view"])
    skip = (page - 1) * limit
    requisitions = inventory_service.get_requisitions(
        db,
        skip=skip,
        limit=limit,
        search=search,
        status_filter=status_filter,
        priority=priority,
        requested_by=requested_by,
        work_order_id=work_order_id,
        production_order_id=production_order_id
    )
    total = inventory_service.get_requisition_count(
        db,
        search=search,
        status_filter=status_filter,
        priority=priority,
        requested_by=requested_by,
        work_order_id=work_order_id,
        production_order_id=production_order_id
    )

    return PaginatedResponse(
        success=True,
        data=requisitions,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/requisitions", response_model=InventoryRequisitionResponse, status_code=status.HTTP_201_CREATED)
async def create_requisition(
    requisition: InventoryRequisitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a draft inventory requisition."""
    require_any_permission(db, current_user, ["inventory.requisitions.create", "inventory.create"])
    return inventory_service.create_requisition(db, requisition, current_user.id)


@router.get("/requisitions/approvers", response_model=List[InventoryRequisitionApproverResponse])
async def list_requisition_approvers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List active users who can be assigned to approve requisitions."""
    require_any_permission(db, current_user, ["inventory.requisitions.create", "inventory.requisitions.submit", "inventory.view"])
    return inventory_service.get_requisition_approvers(db, exclude_user_id=current_user.id)


@router.get("/requisitions/{requisition_id}", response_model=InventoryRequisitionResponse)
async def get_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory requisition details."""
    require_any_permission(db, current_user, ["inventory.requisitions.view", "inventory.view"])
    requisition = inventory_service.get_requisition(db, requisition_id)
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return requisition


@router.put("/requisitions/{requisition_id}", response_model=InventoryRequisitionResponse)
async def update_requisition(
    requisition_id: int,
    requisition: InventoryRequisitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a draft inventory requisition."""
    require_any_permission(db, current_user, ["inventory.requisitions.edit", "inventory.edit"])
    updated = inventory_service.update_requisition(db, requisition_id, requisition)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return updated


@router.post("/requisitions/{requisition_id}/submit", response_model=InventoryRequisitionResponse)
async def submit_requisition(
    requisition_id: int,
    assignment: Optional[InventoryRequisitionApproverAssignmentRequest] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit a draft inventory requisition."""
    require_any_permission(db, current_user, ["inventory.requisitions.submit", "inventory.create"])
    requisition = inventory_service.submit_requisition(
        db,
        requisition_id,
        current_user.id,
        assignment.approver_id if assignment else None,
    )
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return requisition


@router.patch("/requisitions/{requisition_id}/approver", response_model=InventoryRequisitionResponse)
async def assign_requisition_approver(
    requisition_id: int,
    assignment: InventoryRequisitionApproverAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign or reassign an approver for a draft or submitted requisition."""
    require_any_permission(db, current_user, ["inventory.requisitions.approve"])
    requisition = inventory_service.assign_requisition_approver(
        db, requisition_id, assignment.approver_id, current_user.id
    )
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return requisition


@router.post("/requisitions/{requisition_id}/approve", response_model=InventoryRequisitionResponse)
async def approve_requisition(
    requisition_id: int,
    approval: InventoryRequisitionApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve a submitted inventory requisition."""
    require_any_permission(db, current_user, ["inventory.requisitions.approve"])
    requisition = inventory_service.approve_requisition(db, requisition_id, approval, current_user.id)
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return requisition


@router.post("/requisitions/{requisition_id}/reject", response_model=InventoryRequisitionResponse)
async def reject_requisition(
    requisition_id: int,
    rejection: InventoryRequisitionRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reject a submitted inventory requisition."""
    require_any_permission(db, current_user, ["inventory.requisitions.approve"])
    requisition = inventory_service.reject_requisition(db, requisition_id, rejection, current_user.id)
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return requisition


@router.post("/requisitions/{requisition_id}/fulfill", response_model=InventoryRequisitionResponse)
async def fulfill_requisition(
    requisition_id: int,
    fulfillment: InventoryRequisitionFulfillmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fulfill an approved inventory requisition and issue stock."""
    require_any_permission(db, current_user, ["inventory.requisitions.fulfill", "inventory.transaction", "inventory.adjust"])
    requisition = inventory_service.fulfill_requisition(db, requisition_id, fulfillment, current_user.id)
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return requisition


@router.post("/requisitions/{requisition_id}/cancel", response_model=InventoryRequisitionResponse)
async def cancel_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel an inventory requisition before fulfillment starts."""
    require_any_permission(db, current_user, ["inventory.requisitions.cancel", "inventory.edit"])
    requisition = inventory_service.cancel_requisition(db, requisition_id)
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisition not found")
    return requisition


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
