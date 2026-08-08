from typing import List, Optional
from datetime import datetime, timedelta
import re
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.inventory import InventoryItem, InventoryTransaction, TransactionType
from models.sales import (
    Customer, SalesOrder, SalesOrderItem, SalesOrderStatus,
    SalesOrderLineStatus, SalesOrderPriority, SalesInvoice, SalesInvoiceItem,
    SalesReceipt, SalesInvoiceStatus
)
from schemas.sales import (
    CustomerCreate, CustomerUpdate, SalesOrderCreate, SalesOrderUpdate,
    SalesOrderFulfillmentRequest, SalesOrderCancelRequest,
    SalesInvoiceReceiptCreate
)


# ==================== CUSTOMER SERVICES ====================

def generate_customer_code(db: Session) -> str:
    """Generate a unique customer code."""
    next_number = (db.query(func.count(Customer.id)).scalar() or 0) + 1
    while True:
        customer_code = f"CUST-{next_number:04d}"
        if not db.query(Customer).filter(Customer.customer_code == customer_code).first():
            return customer_code
        next_number += 1


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    include_inactive: bool = False,
) -> List[Customer]:
    """Get customers with optional filters."""
    query = db.query(Customer)

    if search:
        query = query.filter(
            or_(
                Customer.customer_code.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                Customer.contact_person.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
            )
        )

    if not include_inactive:
        query = query.filter(Customer.is_active == True)

    return query.order_by(Customer.name).offset(skip).limit(limit).all()


def get_customers_count(
    db: Session,
    search: Optional[str] = None,
    include_inactive: bool = False,
) -> int:
    """Get count of customers with filters."""
    query = db.query(func.count(Customer.id))

    if search:
        query = query.filter(
            or_(
                Customer.customer_code.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                Customer.contact_person.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
            )
        )

    if not include_inactive:
        query = query.filter(Customer.is_active == True)

    return query.scalar()


def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    """Get customer by ID."""
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_code(db: Session, customer_code: str) -> Optional[Customer]:
    """Get customer by code."""
    return db.query(Customer).filter(Customer.customer_code == customer_code).first()


def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    """Create a customer."""
    customer_code = customer.customer_code or generate_customer_code(db)
    if get_customer_by_code(db, customer_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer code already exists",
        )

    customer_data = customer.model_dump()
    customer_data["customer_code"] = customer_code
    db_customer = Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer: CustomerUpdate) -> Optional[Customer]:
    """Update a customer."""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None

    update_data = customer.model_dump(exclude_unset=True)
    if "customer_code" in update_data and update_data["customer_code"]:
        existing = get_customer_by_code(db, update_data["customer_code"])
        if existing and existing.id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer code already exists",
            )

    for field, value in update_data.items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> bool:
    """Delete a customer, or deactivate when orders exist."""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False

    order_count = db.query(func.count(SalesOrder.id)).filter(
        SalesOrder.customer_id == customer_id
    ).scalar()
    if order_count > 0:
        db_customer.is_active = False
    else:
        db.delete(db_customer)

    db.commit()
    return True


# ==================== SALES ORDER SERVICES ====================

def generate_sales_order_number(db: Session) -> str:
    """Generate a human-readable sales order number."""
    prefix = f"SO-{datetime.utcnow().strftime('%Y%m')}"
    count = db.query(func.count(SalesOrder.id)).filter(
        SalesOrder.order_number.ilike(f"{prefix}-%")
    ).scalar()
    return f"{prefix}-{(count or 0) + 1:04d}"


def _get_order_query(db: Session):
    return db.query(SalesOrder).options(
        joinedload(SalesOrder.customer),
        joinedload(SalesOrder.items).joinedload(SalesOrderItem.item),
    )


def get_sales_order(db: Session, order_id: int) -> Optional[SalesOrder]:
    """Get sales order by ID."""
    return _get_order_query(db).filter(SalesOrder.id == order_id).first()


def get_sales_orders_count(
    db: Session,
    search: Optional[str] = None,
    status_filter: Optional[SalesOrderStatus] = None,
    priority: Optional[SalesOrderPriority] = None,
    customer_id: Optional[int] = None,
) -> int:
    """Get count of sales orders with filters."""
    query = db.query(func.count(SalesOrder.id)).outerjoin(Customer)

    if search:
        query = query.filter(
            or_(
                SalesOrder.order_number.ilike(f"%{search}%"),
                Customer.customer_code.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                SalesOrder.notes.ilike(f"%{search}%"),
            )
        )
    if status_filter:
        query = query.filter(SalesOrder.status == status_filter)
    if priority:
        query = query.filter(SalesOrder.priority == priority)
    if customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)

    return query.scalar()


def get_sales_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status_filter: Optional[SalesOrderStatus] = None,
    priority: Optional[SalesOrderPriority] = None,
    customer_id: Optional[int] = None,
) -> List[SalesOrder]:
    """Get sales orders with optional filters."""
    query = _get_order_query(db).outerjoin(Customer)

    if search:
        query = query.filter(
            or_(
                SalesOrder.order_number.ilike(f"%{search}%"),
                Customer.customer_code.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                SalesOrder.notes.ilike(f"%{search}%"),
            )
        )
    if status_filter:
        query = query.filter(SalesOrder.status == status_filter)
    if priority:
        query = query.filter(SalesOrder.priority == priority)
    if customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)

    return query.order_by(SalesOrder.created_at.desc()).offset(skip).limit(limit).all()


def get_sales_statistics(db: Session) -> dict:
    """Get sales dashboard statistics."""
    total_orders = db.query(func.count(SalesOrder.id)).scalar()
    draft = db.query(func.count(SalesOrder.id)).filter(SalesOrder.status == SalesOrderStatus.DRAFT).scalar()
    confirmed = db.query(func.count(SalesOrder.id)).filter(SalesOrder.status == SalesOrderStatus.CONFIRMED).scalar()
    partial = db.query(func.count(SalesOrder.id)).filter(SalesOrder.status == SalesOrderStatus.PARTIALLY_FULFILLED).scalar()
    fulfilled = db.query(func.count(SalesOrder.id)).filter(SalesOrder.status == SalesOrderStatus.FULFILLED).scalar()
    total_revenue = db.query(func.sum(SalesOrder.total_amount)).filter(
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.PARTIALLY_FULFILLED, SalesOrderStatus.FULFILLED])
    ).scalar() or 0
    open_value = db.query(func.sum(SalesOrder.total_amount)).filter(
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.PARTIALLY_FULFILLED])
    ).scalar() or 0
    active_customers = db.query(func.count(Customer.id)).filter(Customer.is_active == True).scalar()

    return {
        "total_orders": total_orders,
        "draft": draft,
        "confirmed": confirmed,
        "partially_fulfilled": partial,
        "fulfilled": fulfilled,
        "total_revenue": round(float(total_revenue), 2),
        "open_value": round(float(open_value), 2),
        "active_customers": active_customers,
    }


def _validate_customer(db: Session, customer_id: int) -> Customer:
    customer = get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer not found",
        )
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer is inactive",
        )
    return customer


def _validate_order_items(db: Session, items: List) -> List[tuple]:
    validated_items = []
    seen_item_ids = set()

    for line in items:
        if line.item_id in seen_item_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate items are not allowed in the same sales order",
            )
        seen_item_ids.add(line.item_id)

        item = db.query(InventoryItem).filter(InventoryItem.id == line.item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Inventory item {line.item_id} not found",
            )
        validated_items.append((line, item))

    return validated_items


def _calculate_line_total(quantity: float, unit_price: float, tax_rate: float, discount_amount: float) -> float:
    subtotal = quantity * unit_price
    tax_amount = subtotal * (tax_rate / 100)
    return round(max(0, subtotal + tax_amount - discount_amount), 2)


def _recalculate_order_totals(order: SalesOrder) -> None:
    subtotal = sum(line.ordered_quantity * line.unit_price for line in order.items)
    tax_amount = sum((line.ordered_quantity * line.unit_price) * (line.tax_rate / 100) for line in order.items)
    discount_amount = sum(line.discount_amount for line in order.items)
    order.subtotal = round(float(subtotal), 2)
    order.tax_amount = round(float(tax_amount), 2)
    order.discount_amount = round(float(discount_amount), 2)
    order.total_amount = round(max(0, order.subtotal + order.tax_amount - order.discount_amount), 2)


def _replace_order_items(db: Session, order: SalesOrder, items: List) -> None:
    validated_items = _validate_order_items(db, items)
    order.items.clear()
    db.flush()

    for line, item in validated_items:
        order.items.append(SalesOrderItem(
            item_id=item.id,
            item_code=item.item_code,
            item_name=item.name,
            ordered_quantity=line.ordered_quantity,
            fulfilled_quantity=0,
            unit_of_measure=item.unit_of_measure,
            unit_price=line.unit_price,
            tax_rate=line.tax_rate,
            discount_amount=line.discount_amount,
            line_total=_calculate_line_total(
                line.ordered_quantity,
                line.unit_price,
                line.tax_rate,
                line.discount_amount,
            ),
            notes=line.notes,
            status=SalesOrderLineStatus.PENDING,
        ))

    _recalculate_order_totals(order)


def create_sales_order(db: Session, order: SalesOrderCreate, created_by: int) -> SalesOrder:
    """Create a draft sales order."""
    _validate_customer(db, order.customer_id)
    db_order = SalesOrder(
        order_number=generate_sales_order_number(db),
        customer_id=order.customer_id,
        priority=order.priority,
        order_date=order.order_date or datetime.utcnow().date().isoformat(),
        requested_delivery_date=order.requested_delivery_date,
        currency=order.currency,
        notes=order.notes,
        created_by=created_by,
        status=SalesOrderStatus.DRAFT,
    )
    db.add(db_order)
    _replace_order_items(db, db_order, order.items)
    db.commit()
    db.refresh(db_order)
    return get_sales_order(db, db_order.id)


def update_sales_order(db: Session, order_id: int, order: SalesOrderUpdate) -> Optional[SalesOrder]:
    """Update a draft sales order."""
    db_order = get_sales_order(db, order_id)
    if not db_order:
        return None
    if db_order.status != SalesOrderStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft sales orders can be edited",
        )

    update_data = order.model_dump(exclude_unset=True, exclude={"items"})
    if "customer_id" in update_data and update_data["customer_id"]:
        _validate_customer(db, update_data["customer_id"])

    for field, value in update_data.items():
        setattr(db_order, field, value)

    if order.items is not None:
        if len(order.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A sales order must include at least one item",
            )
        _replace_order_items(db, db_order, order.items)
    else:
        _recalculate_order_totals(db_order)

    db.commit()
    db.refresh(db_order)
    return get_sales_order(db, db_order.id)


def confirm_sales_order(db: Session, order_id: int, confirmed_by: int) -> Optional[SalesOrder]:
    """Confirm a draft sales order."""
    db_order = get_sales_order(db, order_id)
    if not db_order:
        return None
    if db_order.status != SalesOrderStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft sales orders can be confirmed",
        )
    if not db_order.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A sales order must include at least one item",
        )

    _validate_customer(db, db_order.customer_id)
    db_order.status = SalesOrderStatus.CONFIRMED
    db_order.confirmed_by = confirmed_by
    db_order.confirmed_at = datetime.utcnow()

    db.commit()
    db.refresh(db_order)
    return get_sales_order(db, db_order.id)


def fulfill_sales_order(
    db: Session,
    order_id: int,
    fulfillment: SalesOrderFulfillmentRequest,
    fulfilled_by: int,
) -> Optional[SalesOrder]:
    """Issue stock against a confirmed sales order."""
    db_order = get_sales_order(db, order_id)
    if not db_order:
        return None
    if db_order.status not in [SalesOrderStatus.CONFIRMED, SalesOrderStatus.PARTIALLY_FULFILLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only confirmed sales orders can be fulfilled",
        )

    lines_by_id = {line.id: line for line in db_order.items}
    for fulfillment_line in fulfillment.items:
        line = lines_by_id.get(fulfillment_line.line_id)
        if not line:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fulfillment includes unknown sales order lines",
            )
        remaining_quantity = line.ordered_quantity - line.fulfilled_quantity
        if fulfillment_line.quantity > remaining_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fulfillment quantity exceeds remaining quantity for line {line.id}",
            )
        if line.item.quantity < fulfillment_line.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {line.item_name}",
            )

    for fulfillment_line in fulfillment.items:
        line = lines_by_id[fulfillment_line.line_id]
        line.item.quantity -= fulfillment_line.quantity
        line.fulfilled_quantity += fulfillment_line.quantity

        if line.fulfilled_quantity >= line.ordered_quantity:
            line.status = SalesOrderLineStatus.FULFILLED
        else:
            line.status = SalesOrderLineStatus.PARTIALLY_FULFILLED

        db.add(InventoryTransaction(
            item_id=line.item_id,
            transaction_type=TransactionType.ISSUE,
            quantity=-abs(fulfillment_line.quantity),
            unit_cost=line.item.unit_cost,
            reference_number=db_order.order_number,
            notes=fulfillment.notes or f"Issued for sales order {db_order.order_number}",
            performed_by=fulfilled_by,
        ))

    if all(line.status == SalesOrderLineStatus.FULFILLED for line in db_order.items):
        db_order.status = SalesOrderStatus.FULFILLED
        db_order.fulfilled_at = datetime.utcnow()
    else:
        db_order.status = SalesOrderStatus.PARTIALLY_FULFILLED

    db_order.fulfilled_by = fulfilled_by
    db.commit()
    db.refresh(db_order)
    return get_sales_order(db, db_order.id)


def cancel_sales_order(
    db: Session,
    order_id: int,
    cancellation: SalesOrderCancelRequest,
    cancelled_by: int,
) -> Optional[SalesOrder]:
    """Cancel a sales order before fulfillment starts."""
    db_order = get_sales_order(db, order_id)
    if not db_order:
        return None
    if db_order.status in [SalesOrderStatus.FULFILLED, SalesOrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This sales order cannot be cancelled",
        )
    if any(line.fulfilled_quantity > 0 for line in db_order.items):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a sales order after fulfillment has started",
        )

    db_order.status = SalesOrderStatus.CANCELLED
    db_order.cancelled_by = cancelled_by
    db_order.cancelled_at = datetime.utcnow()
    db_order.cancellation_reason = cancellation.reason
    for line in db_order.items:
        line.status = SalesOrderLineStatus.CANCELLED

    db.commit()
    db.refresh(db_order)
    return get_sales_order(db, db_order.id)


# ==================== INVOICE & RECEIPT SERVICES ====================

def generate_invoice_number(db: Session) -> str:
    prefix = f"INV-{datetime.utcnow().strftime('%Y%m')}"
    count = db.query(func.count(SalesInvoice.id)).filter(
        SalesInvoice.invoice_number.ilike(f"{prefix}-%")
    ).scalar()
    return f"{prefix}-{(count or 0) + 1:04d}"


def generate_receipt_number(db: Session) -> str:
    prefix = f"RCT-{datetime.utcnow().strftime('%Y%m')}"
    count = db.query(func.count(SalesReceipt.id)).filter(
        SalesReceipt.receipt_number.ilike(f"{prefix}-%")
    ).scalar()
    return f"{prefix}-{(count or 0) + 1:04d}"


def _get_invoice_query(db: Session):
    return db.query(SalesInvoice).options(
        joinedload(SalesInvoice.customer),
        joinedload(SalesInvoice.sales_order).joinedload(SalesOrder.customer),
        joinedload(SalesInvoice.sales_order).joinedload(SalesOrder.items),
        joinedload(SalesInvoice.items),
        joinedload(SalesInvoice.receipts),
    )


def get_invoice(db: Session, invoice_id: int) -> Optional[SalesInvoice]:
    return _get_invoice_query(db).filter(SalesInvoice.id == invoice_id).first()


def get_invoice_by_order(db: Session, order_id: int) -> Optional[SalesInvoice]:
    return _get_invoice_query(db).filter(SalesInvoice.sales_order_id == order_id).first()


def get_invoices(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None, status_filter=None, customer_id: Optional[int] = None) -> List[SalesInvoice]:
    query = _get_invoice_query(db).outerjoin(Customer).outerjoin(SalesOrder)
    if search:
        query = query.filter(or_(
            SalesInvoice.invoice_number.ilike(f"%{search}%"),
            SalesOrder.order_number.ilike(f"%{search}%"),
            Customer.name.ilike(f"%{search}%"),
            Customer.customer_code.ilike(f"%{search}%"),
        ))
    if status_filter:
        query = query.filter(SalesInvoice.status == status_filter)
    if customer_id:
        query = query.filter(SalesInvoice.customer_id == customer_id)
    return query.order_by(SalesInvoice.created_at.desc()).offset(skip).limit(limit).all()


def get_invoices_count(db: Session, search: Optional[str] = None, status_filter=None, customer_id: Optional[int] = None) -> int:
    query = db.query(func.count(SalesInvoice.id)).outerjoin(Customer).outerjoin(SalesOrder)
    if search:
        query = query.filter(or_(
            SalesInvoice.invoice_number.ilike(f"%{search}%"),
            SalesOrder.order_number.ilike(f"%{search}%"),
            Customer.name.ilike(f"%{search}%"),
            Customer.customer_code.ilike(f"%{search}%"),
        ))
    if status_filter:
        query = query.filter(SalesInvoice.status == status_filter)
    if customer_id:
        query = query.filter(SalesInvoice.customer_id == customer_id)
    return query.scalar() or 0


def _invoice_due_date(customer: Customer, invoice_date: datetime) -> Optional[datetime]:
    terms = (customer.payment_terms or "").lower()
    match = re.search(r"(\d+)\s*day", terms)
    if match:
        return invoice_date + timedelta(days=int(match.group(1)))
    if "receipt" in terms or "cash" in terms or "immediate" in terms:
        return invoice_date
    return None


def create_invoice(db: Session, order_id: int, issued_by: int) -> Optional[SalesInvoice]:
    order = get_sales_order(db, order_id)
    if not order:
        return None
    existing = get_invoice_by_order(db, order_id)
    if existing:
        return existing
    if order.status in [SalesOrderStatus.DRAFT, SalesOrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoices can only be issued for confirmed or fulfilled sales orders",
        )

    invoice_date = datetime.utcnow()
    invoice = SalesInvoice(
        invoice_number=generate_invoice_number(db),
        sales_order_id=order.id,
        customer_id=order.customer_id,
        status=SalesInvoiceStatus.ISSUED,
        invoice_date=invoice_date,
        due_date=_invoice_due_date(order.customer, invoice_date),
        currency=order.currency,
        subtotal=order.subtotal,
        tax_amount=order.tax_amount,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount,
        amount_paid=0.0,
        balance_due=order.total_amount,
        issued_by=issued_by,
        issued_at=invoice_date,
    )
    db.add(invoice)
    db.flush()
    for line in order.items:
        invoice.items.append(SalesInvoiceItem(
            sales_order_item_id=line.id,
            item_code=line.item_code,
            item_name=line.item_name,
            quantity=line.ordered_quantity,
            unit_of_measure=line.unit_of_measure,
            unit_price=line.unit_price,
            tax_rate=line.tax_rate,
            discount_amount=line.discount_amount,
            line_total=line.line_total,
            notes=line.notes,
        ))
    db.commit()
    return get_invoice(db, invoice.id)


def create_receipt(db: Session, invoice_id: int, receipt: SalesInvoiceReceiptCreate, received_by: int) -> Optional[SalesInvoice]:
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None
    if invoice.status == SalesInvoiceStatus.VOIDED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voided invoices cannot receive payments")

    amount = round(float(receipt.amount), 2)
    if amount > round(invoice.balance_due, 2) + 0.005:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Receipt amount cannot exceed the invoice balance of {invoice.balance_due:.2f}",
        )

    db.add(SalesReceipt(
        receipt_number=generate_receipt_number(db),
        invoice_id=invoice.id,
        receipt_date=receipt.receipt_date or datetime.utcnow(),
        amount=amount,
        payment_method=receipt.payment_method,
        reference=receipt.reference,
        received_by=received_by,
        notes=receipt.notes,
    ))
    invoice.amount_paid = round(invoice.amount_paid + amount, 2)
    invoice.balance_due = round(max(0.0, invoice.total_amount - invoice.amount_paid), 2)
    invoice.status = SalesInvoiceStatus.PAID if invoice.balance_due <= 0.005 else SalesInvoiceStatus.PARTIALLY_PAID
    db.commit()
    return get_invoice(db, invoice.id)


def void_invoice(db: Session, invoice_id: int, voided_by: int, reason: Optional[str] = None) -> Optional[SalesInvoice]:
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None
    if invoice.amount_paid > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invoices with receipts cannot be voided")
    if invoice.status == SalesInvoiceStatus.VOIDED:
        return invoice
    invoice.status = SalesInvoiceStatus.VOIDED
    invoice.voided_by = voided_by
    invoice.voided_at = datetime.utcnow()
    invoice.notes = reason or invoice.notes
    db.commit()
    return get_invoice(db, invoice.id)
