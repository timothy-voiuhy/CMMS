from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from models.user import User
from models.production import ProductionLineStatus, ProductionOrderStatus
from schemas.production import (
    ProductionLineCreate, ProductionLineUpdate, ProductionLineResponse,
    ProductionLineEquipmentCreate, ProductionLineEquipmentUpdate, ProductionLineEquipmentResponse,
    ShiftCreate, ShiftUpdate, ShiftResponse,
    ProductionOrderCreate, ProductionOrderUpdate, ProductionOrderResponse,
    PackagingOrderCreate, PackagingOrderUpdate, PackagingOrderResponse
)
from schemas.common import PaginatedResponse
from services import production_service

router = APIRouter()


# Production Line Endpoints
@router.get("/lines/statistics")
async def get_line_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get production line statistics."""
    return production_service.get_production_line_statistics(db)


@router.get("/lines", response_model=PaginatedResponse[ProductionLineResponse])
async def list_production_lines(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[ProductionLineStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all production lines."""
    skip = (page - 1) * limit
    lines = production_service.get_production_lines(db, skip=skip, limit=limit, search=search, status=status)
    total = production_service.get_production_lines_count(db, search=search, status=status)
    
    return PaginatedResponse(
        success=True,
        data=lines,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/lines", response_model=ProductionLineResponse, status_code=status.HTTP_201_CREATED)
async def create_production_line(
    line: ProductionLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new production line."""
    return production_service.create_production_line(db, line)


@router.get("/lines/{line_id}", response_model=ProductionLineResponse)
async def get_production_line(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get production line by ID."""
    line = production_service.get_production_line(db, line_id)
    if not line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production line not found")
    return line


@router.put("/lines/{line_id}", response_model=ProductionLineResponse)
async def update_production_line(
    line_id: int,
    line: ProductionLineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update production line."""
    updated = production_service.update_production_line(db, line_id, line)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production line not found")
    return updated


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_production_line(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete production line."""
    deleted = production_service.delete_production_line(db, line_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production line not found")


# Shift Endpoints
@router.get("/lines/{line_id}/shifts", response_model=List[ShiftResponse])
async def list_shifts_by_line(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all shifts for a production line."""
    return production_service.get_shifts_by_line(db, line_id)


@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    shift: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new shift."""
    return production_service.create_shift(db, shift)


@router.get("/shifts/{shift_id}", response_model=ShiftResponse)
async def get_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get shift by ID."""
    shift = production_service.get_shift(db, shift_id)
    if not shift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    return shift


@router.put("/shifts/{shift_id}", response_model=ShiftResponse)
async def update_shift(
    shift_id: int,
    shift: ShiftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update shift."""
    updated = production_service.update_shift(db, shift_id, shift)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
    return updated


@router.delete("/shifts/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete shift."""
    deleted = production_service.delete_shift(db, shift_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")


# Production Line Equipment Station Endpoints
@router.get("/lines/{line_id}/equipment", response_model=List[ProductionLineEquipmentResponse])
async def list_line_equipment_stations(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all equipment stations for a production line in sequence order with enriched data."""
    from sqlalchemy.orm import joinedload
    
    stations = production_service.get_line_equipment_stations(db, line_id)
    
    # Enrich with equipment and craftsmen data
    from models.equipment import Equipment
    from models.craftsman import Craftsman
    from models.user import User as UserModel
    
    enriched_stations = []
    for station in stations:
        station_dict = ProductionLineEquipmentResponse.model_validate(station).model_dump()
        
        # Get equipment details
        equipment = db.query(Equipment).filter(Equipment.id == station.equipment_id).first()
        if equipment:
            station_dict['equipment'] = {
                'id': equipment.id,
                'name': equipment.name,
                'equipment_id': equipment.equipment_id,
                'status': equipment.status.value if equipment.status else None,
                'location': equipment.location,
            }
        
        # Get operators details with user data
        if station.operators:
            operators_data = []
            for operator_id in station.operators:
                craftsman = db.query(Craftsman).options(
                    joinedload(Craftsman.user)
                ).filter(Craftsman.id == operator_id).first()
                
                if craftsman and craftsman.user:
                    operators_data.append({
                        'id': craftsman.id,
                        'employee_id': craftsman.employee_id,
                        'full_name': craftsman.user.full_name,
                        'position': craftsman.position,
                    })
            station_dict['operators_data'] = operators_data
        
        enriched_stations.append(station_dict)
    
    return enriched_stations


@router.post("/lines/{line_id}/equipment", response_model=ProductionLineEquipmentResponse, status_code=status.HTTP_201_CREATED)
async def add_equipment_to_line(
    line_id: int,
    station: ProductionLineEquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add equipment station to a production line."""
    # Ensure the line_id in the path matches the one in the body
    if station.production_line_id != line_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Production line ID mismatch"
        )
    return production_service.create_line_equipment_station(db, station)


@router.put("/equipment-stations/{station_id}", response_model=ProductionLineEquipmentResponse)
async def update_equipment_station(
    station_id: int,
    station: ProductionLineEquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update equipment station configuration."""
    updated = production_service.update_line_equipment_station(db, station_id, station)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment station not found")
    return updated


@router.delete("/equipment-stations/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_equipment_from_line(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove equipment station from production line."""
    deleted = production_service.delete_line_equipment_station(db, station_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment station not found")


@router.post("/lines/{line_id}/equipment/reorder", response_model=List[ProductionLineEquipmentResponse])
async def reorder_equipment_stations(
    line_id: int,
    station_orders: List[dict] = Body(..., example=[{"id": 1, "sequence_order": 1}]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reorder equipment stations on a production line."""
    return production_service.reorder_line_equipment_stations(db, line_id, station_orders)


# Production Order Endpoints
@router.get("/orders/statistics")
async def get_order_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get production order statistics."""
    return production_service.get_production_order_statistics(db)


@router.get("/orders", response_model=PaginatedResponse[ProductionOrderResponse])
async def list_production_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[ProductionOrderStatus] = None,
    line_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all production orders."""
    skip = (page - 1) * limit
    orders = production_service.get_production_orders(
        db, skip=skip, limit=limit, search=search, status=status, line_id=line_id
    )
    total = production_service.get_production_orders_count(
        db, search=search, status=status, line_id=line_id
    )
    
    return PaginatedResponse(
        success=True,
        data=orders,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/orders", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_production_order(
    order: ProductionOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new production order."""
    return production_service.create_production_order(db, order)


@router.get("/orders/{order_id}", response_model=ProductionOrderResponse)
async def get_production_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get production order by ID."""
    order = production_service.get_production_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production order not found")
    return order


@router.put("/orders/{order_id}", response_model=ProductionOrderResponse)
async def update_production_order(
    order_id: int,
    order: ProductionOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update production order."""
    updated = production_service.update_production_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production order not found")
    return updated


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_production_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete production order."""
    deleted = production_service.delete_production_order(db, order_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production order not found")


# Packaging Order Endpoints
@router.get("/packaging/statistics")
async def get_packaging_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get packaging order statistics."""
    return production_service.get_packaging_order_statistics(db)


@router.get("/packaging", response_model=PaginatedResponse[PackagingOrderResponse])
async def list_packaging_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[ProductionOrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all packaging orders."""
    skip = (page - 1) * limit
    orders = production_service.get_packaging_orders(db, skip=skip, limit=limit, search=search, status=status)
    total = production_service.get_packaging_orders_count(db, search=search, status=status)
    
    return PaginatedResponse(
        success=True,
        data=orders,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/packaging", response_model=PackagingOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_packaging_order(
    order: PackagingOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new packaging order."""
    return production_service.create_packaging_order(db, order)


@router.get("/packaging/{order_id}", response_model=PackagingOrderResponse)
async def get_packaging_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get packaging order by ID."""
    order = production_service.get_packaging_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packaging order not found")
    return order


@router.put("/packaging/{order_id}", response_model=PackagingOrderResponse)
async def update_packaging_order(
    order_id: int,
    order: PackagingOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update packaging order."""
    updated = production_service.update_packaging_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packaging order not found")
    return updated


@router.delete("/packaging/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_packaging_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete packaging order."""
    deleted = production_service.delete_packaging_order(db, order_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packaging order not found")
