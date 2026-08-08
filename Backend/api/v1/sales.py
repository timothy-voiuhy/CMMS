from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from models.sales import SalesOrderStatus, SalesOrderPriority, SalesInvoiceStatus
from schemas.common import PaginatedResponse
from schemas.sales import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    SalesOrderCreate, SalesOrderUpdate, SalesOrderResponse, SalesOrderListResponse,
    SalesOrderFulfillmentRequest, SalesOrderCancelRequest,
    SalesInvoiceResponse, SalesInvoiceReceiptCreate, SalesInvoiceVoidRequest,
)
from services import sales_service
from services.company_service import get_user_permissions

router = APIRouter()


def require_any_permission(db: Session, current_user: User, permissions: List[str]) -> None:
    """Require any matching resolved permission for sales actions."""
    user_permissions = set(get_user_permissions(db, current_user.id))
    if (
        "*" in user_permissions
        or "admin.full_access" in user_permissions
        or any(permission in user_permissions for permission in permissions)
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions",
    )


@router.get("/statistics")
async def get_sales_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get sales statistics."""
    require_any_permission(db, current_user, ["sales.view", "sales.orders.view"])
    return sales_service.get_sales_statistics(db)


# ==================== CUSTOMER ENDPOINTS ====================

@router.get("/customers", response_model=PaginatedResponse[CustomerResponse])
async def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get customers with optional filters."""
    require_any_permission(db, current_user, ["sales.customers.view", "sales.view"])
    skip = (page - 1) * limit
    customers = sales_service.get_customers(
        db,
        skip=skip,
        limit=limit,
        search=search,
        include_inactive=include_inactive,
    )
    total = sales_service.get_customers_count(
        db,
        search=search,
        include_inactive=include_inactive,
    )
    return PaginatedResponse(
        success=True,
        data=customers,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit,
    )


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a customer."""
    require_any_permission(db, current_user, ["sales.customers.create"])
    return sales_service.create_customer(db, customer)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get customer by ID."""
    require_any_permission(db, current_user, ["sales.customers.view", "sales.view"])
    customer = sales_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a customer."""
    require_any_permission(db, current_user, ["sales.customers.edit"])
    updated = sales_service.update_customer(db, customer_id, customer)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return updated


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete or deactivate a customer."""
    require_any_permission(db, current_user, ["sales.customers.delete"])
    deleted = sales_service.delete_customer(db, customer_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")


# ==================== SALES ORDER ENDPOINTS ====================

@router.get("/orders", response_model=PaginatedResponse[SalesOrderListResponse])
async def list_sales_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[SalesOrderStatus] = Query(None, alias="status"),
    priority: Optional[SalesOrderPriority] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get sales orders with optional filters."""
    require_any_permission(db, current_user, ["sales.orders.view", "sales.view"])
    skip = (page - 1) * limit
    orders = sales_service.get_sales_orders(
        db,
        skip=skip,
        limit=limit,
        search=search,
        status_filter=status_filter,
        priority=priority,
        customer_id=customer_id,
    )
    total = sales_service.get_sales_orders_count(
        db,
        search=search,
        status_filter=status_filter,
        priority=priority,
        customer_id=customer_id,
    )
    return PaginatedResponse(
        success=True,
        data=orders,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit,
    )


@router.post("/orders", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    order: SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a draft sales order."""
    require_any_permission(db, current_user, ["sales.orders.create"])
    return sales_service.create_sales_order(db, order, current_user.id)


@router.get("/orders/{order_id}", response_model=SalesOrderResponse)
async def get_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get sales order details."""
    require_any_permission(db, current_user, ["sales.orders.view", "sales.view"])
    order = sales_service.get_sales_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    return order


@router.put("/orders/{order_id}", response_model=SalesOrderResponse)
async def update_sales_order(
    order_id: int,
    order: SalesOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a draft sales order."""
    require_any_permission(db, current_user, ["sales.orders.edit"])
    updated = sales_service.update_sales_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    return updated


@router.post("/orders/{order_id}/confirm", response_model=SalesOrderResponse)
async def confirm_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Confirm a draft sales order."""
    require_any_permission(db, current_user, ["sales.orders.confirm"])
    order = sales_service.confirm_sales_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    return order


@router.post("/orders/{order_id}/fulfill", response_model=SalesOrderResponse)
async def fulfill_sales_order(
    order_id: int,
    fulfillment: SalesOrderFulfillmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Fulfill a confirmed sales order and issue stock."""
    require_any_permission(db, current_user, ["sales.orders.fulfill", "inventory.transaction"])
    order = sales_service.fulfill_sales_order(db, order_id, fulfillment, current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    return order


@router.post("/orders/{order_id}/cancel", response_model=SalesOrderResponse)
async def cancel_sales_order(
    order_id: int,
    cancellation: SalesOrderCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel a sales order before fulfillment starts."""
    require_any_permission(db, current_user, ["sales.orders.cancel"])
    order = sales_service.cancel_sales_order(db, order_id, cancellation, current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    return order


# ==================== INVOICE & RECEIPT ENDPOINTS ====================

@router.get("/invoices", response_model=PaginatedResponse[SalesInvoiceResponse])
async def list_invoices(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[SalesInvoiceStatus] = Query(None, alias="status"),
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    require_any_permission(db, current_user, ["sales.invoices.view", "sales.view"])
    skip = (page - 1) * limit
    invoices = sales_service.get_invoices(db, skip, limit, search, status_filter, customer_id)
    total = sales_service.get_invoices_count(db, search, status_filter, customer_id)
    return PaginatedResponse(
        success=True,
        data=invoices,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit,
    )


@router.post("/orders/{order_id}/invoice", response_model=SalesInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def issue_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    require_any_permission(db, current_user, ["sales.invoices.create"])
    invoice = sales_service.create_invoice(db, order_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    return invoice


@router.get("/orders/{order_id}/invoice", response_model=SalesInvoiceResponse)
async def get_order_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    require_any_permission(db, current_user, ["sales.invoices.view", "sales.view"])
    invoice = sales_service.get_invoice_by_order(db, order_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@router.get("/invoices/{invoice_id}", response_model=SalesInvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    require_any_permission(db, current_user, ["sales.invoices.view", "sales.view"])
    invoice = sales_service.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@router.post("/invoices/{invoice_id}/receipts", response_model=SalesInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def record_receipt(
    invoice_id: int,
    receipt: SalesInvoiceReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    require_any_permission(db, current_user, ["sales.receipts.create"])
    invoice = sales_service.create_receipt(db, invoice_id, receipt, current_user.id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@router.post("/invoices/{invoice_id}/void", response_model=SalesInvoiceResponse)
async def void_invoice(
    invoice_id: int,
    request: SalesInvoiceVoidRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    require_any_permission(db, current_user, ["sales.invoices.void"])
    invoice = sales_service.void_invoice(db, invoice_id, current_user.id, request.reason)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice
