from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from models.work_order import WorkOrderStatus, WorkOrderPriority
from schemas.work_order import (
    WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse,
    WorkOrderStatusUpdate, WorkOrderAssign
)
from schemas.common import PaginatedResponse
from services import work_order_service

router = APIRouter()


@router.get("/statistics")
async def get_work_order_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work order statistics."""
    return work_order_service.get_work_order_statistics(db)


@router.get("/", response_model=PaginatedResponse[WorkOrderResponse])
async def list_work_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[WorkOrderStatus] = None,
    priority: Optional[WorkOrderPriority] = None,
    assigned_to: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all work orders with optional filters."""
    skip = (page - 1) * limit
    work_orders = work_order_service.get_work_orders(
        db, skip=skip, limit=limit, search=search,
        status_filter=status, priority=priority, assigned_to=assigned_to
    )
    total = work_order_service.get_work_orders_count(
        db, search=search, status_filter=status, priority=priority, assigned_to=assigned_to
    )
    
    return PaginatedResponse(
        success=True,
        data=work_orders,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new work order."""
    return work_order_service.create_work_order(db, work_order, current_user.id)


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work order by ID."""
    work_order = work_order_service.get_work_order(db, work_order_id)
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return work_order


@router.put("/{work_order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    work_order_id: int,
    work_order: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update work order."""
    updated = work_order_service.update_work_order(db, work_order_id, work_order)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return updated


@router.delete("/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete work order."""
    deleted = work_order_service.delete_work_order(db, work_order_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")


@router.post("/{work_order_id}/assign", response_model=WorkOrderResponse)
async def assign_work_order(
    work_order_id: int,
    assignment: WorkOrderAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign work order to a craftsman."""
    work_order = work_order_service.assign_work_order(db, work_order_id, assignment.craftsman_id)
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return work_order


@router.patch("/{work_order_id}/status", response_model=WorkOrderResponse)
async def update_status(
    work_order_id: int,
    status_update: WorkOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update work order status."""
    work_order = work_order_service.update_work_order_status(
        db, work_order_id, status_update.status, status_update.notes
    )
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return work_order


@router.get("/by-craftsman/{craftsman_id}", response_model=List[WorkOrderResponse])
async def get_craftsman_work_orders(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work orders assigned to a craftsman."""
    return work_order_service.get_craftsman_work_orders(db, craftsman_id)


@router.get("/by-equipment/{equipment_id}", response_model=List[WorkOrderResponse])
async def get_equipment_work_orders(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work orders for an equipment."""
    return work_order_service.get_equipment_work_orders(db, equipment_id)
