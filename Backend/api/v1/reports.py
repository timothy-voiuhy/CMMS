from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, case
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from models.equipment import Equipment
from models.inventory import InventoryItem, InventoryTransaction, InventoryCategory
from models.maintenance import MaintenanceReport
from models.work_order import WorkOrder
from models.production import ProductionOrder, ProductionLine
from models.quality import QualityInspection, NonConformanceReport
from models.craftsman import Craftsman

router = APIRouter()


# ============= Equipment Reports =============

@router.get("/equipment/summary")
async def get_equipment_summary_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment summary statistics."""
    
    total_equipment = db.query(func.count(Equipment.id)).scalar()
    
    by_status = db.query(
        Equipment.status,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.status).all()
    
    by_type = db.query(
        Equipment.category,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.category).all()
    
    avg_utilization = 0  # Equipment model doesn't have utilization tracking
    
    critical_equipment = db.query(func.count(Equipment.id)).filter(
        Equipment.status == 'operational'
    ).scalar()
    
    return {
        "total_equipment": total_equipment,
        "by_status": [{"status": str(s), "count": c} for s, c in by_status],
        "by_type": [{"type": t or "Unknown", "count": c} for t, c in by_type],
        "average_utilization": round(float(avg_utilization), 2),
        "critical_equipment": critical_equipment
    }


@router.get("/equipment/utilization")
async def get_equipment_utilization_report(
    days: int = Query(default=30, ge=1, le=365),
    equipment_category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment utilization report."""
    
    query = db.query(
        Equipment.equipment_id,
        Equipment.name,
        Equipment.category,
        Equipment.status
    )
    
    if equipment_category:
        query = query.filter(Equipment.category == equipment_category)
    
    equipment = query.all()
    
    return {
        "period_days": days,
        "equipment": [
            {
                "code": e.equipment_id,
                "name": e.name,
                "type": e.category or "Unknown",
                "utilization": 0,  # Would need actual usage tracking
                "status": e.status
            }
            for e in equipment
        ]
    }


# ============= Maintenance Reports =============

@router.get("/maintenance/summary")
async def get_maintenance_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance summary statistics from work orders."""
    
    # Parse date strings
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)
    else:
        end_date_obj = datetime.now()
    
    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)
    else:
        start_date_obj = end_date_obj - timedelta(days=30)
    
    # Use work orders for maintenance statistics
    query = db.query(WorkOrder).filter(
        WorkOrder.created_at >= start_date_obj.isoformat(),
        WorkOrder.created_at <= end_date_obj.isoformat()
    )
    
    total_maintenance = query.count()
    
    by_type = db.query(
        WorkOrder.work_order_type,
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date_obj.isoformat(),
        WorkOrder.created_at <= end_date_obj.isoformat()
    ).group_by(WorkOrder.work_order_type).all()
    
    by_priority = db.query(
        WorkOrder.priority,
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date_obj.isoformat(),
        WorkOrder.created_at <= end_date_obj.isoformat()
    ).group_by(WorkOrder.priority).all()
    
    avg_hours = db.query(
        func.avg(WorkOrder.actual_hours)
    ).filter(
        WorkOrder.created_at >= start_date_obj.isoformat(),
        WorkOrder.created_at <= end_date_obj.isoformat(),
        WorkOrder.actual_hours.isnot(None)
    ).scalar() or 0
    
    return {
        "start_date": start_date_obj.isoformat(),
        "end_date": end_date_obj.isoformat(),
        "total_maintenance": total_maintenance,
        "by_type": [{"type": str(t), "count": c} for t, c in by_type],
        "by_priority": [{"priority": str(p), "count": c} for p, c in by_priority],
        "average_cost": round(float(avg_hours) * 50, 2)  # Estimate: $50/hour
    }


@router.get("/maintenance/downtime")
async def get_maintenance_downtime_report(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment downtime report from work orders."""
    
    start_date_obj = datetime.now() - timedelta(days=days)
    
    maintenance_records = db.query(
        Equipment.equipment_id,
        Equipment.name,
        func.count(WorkOrder.id).label('maintenance_count'),
        func.sum(WorkOrder.actual_hours).label('total_downtime')
    ).join(
        WorkOrder, Equipment.id == WorkOrder.equipment_id
    ).filter(
        WorkOrder.created_at >= start_date_obj.isoformat()
    ).group_by(
        Equipment.id, Equipment.equipment_id, Equipment.name
    ).all()
    
    return {
        "period_days": days,
        "equipment_downtime": [
            {
                "equipment_code": r.equipment_id,
                "equipment_name": r.name,
                "maintenance_count": r.maintenance_count,
                "total_downtime_hours": float(r.total_downtime or 0)
            }
            for r in maintenance_records
        ]
    }


# ============= Inventory Reports =============

@router.get("/inventory/summary")
async def get_inventory_summary_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory summary statistics."""
    
    total_items = db.query(func.count(InventoryItem.id)).scalar()
    
    total_value = db.query(
        func.sum(InventoryItem.quantity * InventoryItem.unit_cost)
    ).scalar() or 0
    
    low_stock_items = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.reorder_point.isnot(None),
        InventoryItem.quantity <= InventoryItem.reorder_point
    ).scalar()
    
    out_of_stock = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.quantity == 0
    ).scalar()
    
    # Get category names via join
    by_category = db.query(
        InventoryCategory.name,
        func.count(InventoryItem.id).label('count'),
        func.sum(InventoryItem.quantity * InventoryItem.unit_cost).label('value')
    ).join(
        InventoryItem, InventoryCategory.id == InventoryItem.category_id
    ).group_by(InventoryCategory.name).all()
    
    return {
        "total_items": total_items,
        "total_value": round(float(total_value), 2),
        "low_stock_items": low_stock_items,
        "out_of_stock": out_of_stock,
        "by_category": [
            {
                "category": c,
                "count": count,
                "value": round(float(value or 0), 2)
            }
            for c, count, value in by_category
        ]
    }


@router.get("/inventory/movements")
async def get_inventory_movements_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory movements/transactions report."""
    
    # Parse date strings
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)
    else:
        end_date_obj = datetime.now()
    
    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)
    else:
        start_date_obj = end_date_obj - timedelta(days=30)
    
    query = db.query(
        InventoryTransaction.transaction_type,
        func.count(InventoryTransaction.id).label('count'),
        func.sum(InventoryTransaction.quantity).label('total_quantity')
    ).filter(
        InventoryTransaction.transaction_date >= start_date_obj,
        InventoryTransaction.transaction_date <= end_date_obj
    )
    
    if transaction_type:
        query = query.filter(InventoryTransaction.transaction_type == transaction_type)
    
    transactions = query.group_by(InventoryTransaction.transaction_type).all()
    
    return {
        "start_date": start_date_obj.isoformat(),
        "end_date": end_date_obj.isoformat(),
        "transactions": [
            {
                "type": t,
                "count": c,
                "total_quantity": float(q or 0)
            }
            for t, c, q in transactions
        ]
    }


@router.get("/inventory/low-stock")
async def get_low_stock_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get low stock items report."""
    
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.reorder_point.isnot(None),
        InventoryItem.quantity <= InventoryItem.reorder_point
    ).all()
    
    # Get category names
    result_items = []
    for item in low_stock_items:
        category_name = db.query(InventoryCategory.name).filter(
            InventoryCategory.id == item.category_id
        ).scalar() or "Unknown"
        
        result_items.append({
            "id": item.id,
            "item_code": item.item_code,
            "name": item.name,
            "category": category_name,
            "quantity": item.quantity,
            "unit": item.unit_of_measure,
            "reorder_level": item.reorder_point,
            "reorder_quantity": item.max_quantity or 0,
            "shortage": item.reorder_point - item.quantity if item.reorder_point else 0
        })
    
    return {
        "low_stock_items": result_items
    }


# ============= Production Reports =============

@router.get("/production/summary")
async def get_production_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get production summary statistics."""
    
    # Parse date strings
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)
    else:
        end_date_obj = datetime.now()
    
    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)
    else:
        start_date_obj = end_date_obj - timedelta(days=30)
    
    total_orders = db.query(func.count(ProductionOrder.id)).filter(
        ProductionOrder.created_at >= start_date_obj,
        ProductionOrder.created_at <= end_date_obj
    ).scalar()
    
    by_status = db.query(
        ProductionOrder.status,
        func.count(ProductionOrder.id).label('count')
    ).filter(
        ProductionOrder.created_at >= start_date_obj.isoformat(),
        ProductionOrder.created_at <= end_date_obj.isoformat()
    ).group_by(ProductionOrder.status).all()
    
    total_quantity = db.query(
        func.sum(ProductionOrder.produced_quantity)
    ).filter(
        ProductionOrder.created_at >= start_date_obj.isoformat(),
        ProductionOrder.created_at <= end_date_obj.isoformat()
    ).scalar() or 0
    
    active_lines = db.query(func.count(ProductionLine.id)).filter(
        ProductionLine.status == 'active'
    ).scalar()
    
    return {
        "start_date": start_date_obj.isoformat(),
        "end_date": end_date_obj.isoformat(),
        "total_orders": total_orders,
        "by_status": [{"status": str(s), "count": c} for s, c in by_status],
        "total_quantity_produced": float(total_quantity),
        "active_lines": active_lines
    }


@router.get("/production/efficiency")
async def get_production_efficiency_report(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get production efficiency report."""
    
    start_date_obj = datetime.now() - timedelta(days=days)
    
    production_data = db.query(
        ProductionLine.line_code,
        ProductionLine.name,
        func.count(ProductionOrder.id).label('orders_count'),
        func.sum(ProductionOrder.produced_quantity).label('total_produced'),
        func.avg(
            case(
                (ProductionOrder.target_quantity > 0,
                 (ProductionOrder.produced_quantity / ProductionOrder.target_quantity) * 100),
                else_=0
            )
        ).label('avg_efficiency')
    ).join(
        ProductionOrder, ProductionLine.id == ProductionOrder.production_line_id
    ).filter(
        ProductionOrder.created_at >= start_date_obj.isoformat()
    ).group_by(
        ProductionLine.id, ProductionLine.line_code, ProductionLine.name
    ).all()
    
    return {
        "period_days": days,
        "production_lines": [
            {
                "line_code": p.line_code,
                "line_name": p.name,
                "orders_count": p.orders_count,
                "total_produced": float(p.total_produced or 0),
                "average_efficiency": round(float(p.avg_efficiency or 0), 2)
            }
            for p in production_data
        ]
    }


# ============= Quality Reports =============

@router.get("/quality/summary")
async def get_quality_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get quality summary statistics."""
    
    # Parse date strings
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)
    else:
        end_date_obj = datetime.now()
    
    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)
    else:
        start_date_obj = end_date_obj - timedelta(days=30)
    
    total_inspections = db.query(func.count(QualityInspection.id)).filter(
        QualityInspection.inspection_date >= start_date_obj,
        QualityInspection.inspection_date <= end_date_obj
    ).scalar()
    
    by_result = db.query(
        QualityInspection.result,
        func.count(QualityInspection.id).label('count')
    ).filter(
        QualityInspection.inspection_date >= start_date_obj,
        QualityInspection.inspection_date <= end_date_obj
    ).group_by(QualityInspection.result).all()
    
    total_ncrs = db.query(func.count(NonConformanceReport.id)).filter(
        NonConformanceReport.created_at >= start_date_obj,
        NonConformanceReport.created_at <= end_date_obj
    ).scalar()
    
    ncrs_by_severity = db.query(
        NonConformanceReport.severity,
        func.count(NonConformanceReport.id).label('count')
    ).filter(
        NonConformanceReport.created_at >= start_date_obj,
        NonConformanceReport.created_at <= end_date_obj
    ).group_by(NonConformanceReport.severity).all()
    
    pass_rate = 0
    if total_inspections > 0:
        passed = db.query(func.count(QualityInspection.id)).filter(
            QualityInspection.inspection_date >= start_date_obj,
            QualityInspection.inspection_date <= end_date_obj,
            QualityInspection.result == 'pass'
        ).scalar()
        pass_rate = (passed / total_inspections) * 100
    
    return {
        "start_date": start_date_obj.isoformat(),
        "end_date": end_date_obj.isoformat(),
        "total_inspections": total_inspections,
        "by_result": [{"result": str(r), "count": c} for r, c in by_result],
        "total_ncrs": total_ncrs,
        "ncrs_by_severity": [{"severity": str(s), "count": c} for s, c in ncrs_by_severity],
        "pass_rate": round(pass_rate, 2)
    }


# ============= Work Order Reports =============

@router.get("/work-orders/summary")
async def get_work_orders_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work orders summary statistics."""
    
    # Parse date strings
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)
    else:
        end_date_obj = datetime.now()
    
    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)
    else:
        start_date_obj = end_date_obj - timedelta(days=30)
    
    total_work_orders = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.created_at >= start_date_obj,
        WorkOrder.created_at <= end_date_obj
    ).scalar()
    
    by_status = db.query(
        WorkOrder.status,
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date_obj,
        WorkOrder.created_at <= end_date_obj
    ).group_by(WorkOrder.status).all()
    
    by_priority = db.query(
        WorkOrder.priority,
        func.count(WorkOrder.id).label('count')
    ).filter(
        WorkOrder.created_at >= start_date_obj,
        WorkOrder.created_at <= end_date_obj
    ).group_by(WorkOrder.priority).all()
    
    # WorkOrder.due_date is stored as an ISO date string (not a timestamp).
    # Compare like-for-like to avoid PostgreSQL's varchar/timestamp type error.
    today_string = datetime.now().strftime("%Y-%m-%d")
    overdue = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.created_at >= start_date_obj,
        WorkOrder.created_at <= end_date_obj,
        WorkOrder.due_date < today_string,
        WorkOrder.status.in_(['pending', 'in_progress'])
    ).scalar()
    
    return {
        "start_date": start_date_obj.isoformat(),
        "end_date": end_date_obj.isoformat(),
        "total_work_orders": total_work_orders,
        "by_status": [{"status": s, "count": c} for s, c in by_status],
        "by_priority": [{"priority": p, "count": c} for p, c in by_priority],
        "overdue": overdue
    }


# ============= Personnel Reports =============

@router.get("/personnel/summary")
async def get_personnel_summary_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get personnel summary statistics."""
    
    total_craftsmen = db.query(func.count(Craftsman.id)).scalar()
    
    by_department = db.query(
        Craftsman.department,
        func.count(Craftsman.id).label('count')
    ).group_by(Craftsman.department).all()
    
    active_craftsmen = db.query(func.count(Craftsman.id)).filter(
        Craftsman.user_id.isnot(None)
    ).scalar()
    
    return {
        "total_craftsmen": total_craftsmen,
        "active_craftsmen": active_craftsmen,
        "by_specialization": [{"specialization": d or "Unknown", "count": c} for d, c in by_department],
        "average_experience_years": 5.0  # Would need hire_date calculation
    }


# ============= Financial Reports =============

@router.get("/financial/summary")
async def get_financial_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get financial summary statistics."""
    
    # Parse date strings
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)
    else:
        end_date_obj = datetime.now()
    
    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)
    else:
        start_date_obj = end_date_obj - timedelta(days=30)
    
    # Maintenance costs (estimated from work orders)
    total_hours = db.query(
        func.sum(WorkOrder.actual_hours)
    ).filter(
        WorkOrder.created_at >= start_date_obj.isoformat(),
        WorkOrder.created_at <= end_date_obj.isoformat(),
        WorkOrder.actual_hours.isnot(None)
    ).scalar() or 0
    
    maintenance_cost = float(total_hours) * 50  # Estimate: $50/hour
    
    # Inventory value
    inventory_value = db.query(
        func.sum(InventoryItem.quantity * InventoryItem.unit_cost)
    ).scalar() or 0
    
    # Inventory transactions value
    inventory_transactions = db.query(
        InventoryTransaction.transaction_type,
        func.sum(InventoryTransaction.quantity * InventoryTransaction.unit_cost).label('value')
    ).filter(
        InventoryTransaction.created_at >= start_date_obj.isoformat(),
        InventoryTransaction.created_at <= end_date_obj.isoformat()
    ).group_by(InventoryTransaction.transaction_type).all()
    
    return {
        "start_date": start_date_obj.isoformat(),
        "end_date": end_date_obj.isoformat(),
        "maintenance_cost": round(maintenance_cost, 2),
        "inventory_value": round(float(inventory_value), 2),
        "inventory_transactions": [
            {
                "type": str(t),
                "value": round(float(v or 0), 2)
            }
            for t, v in inventory_transactions
        ]
    }
