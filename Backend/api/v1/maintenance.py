from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from core.config import settings
from models.user import User
from models.maintenance import MaintenanceCatalogueItemType
from schemas.maintenance import (
    MaintenanceReportCreate, MaintenanceReportUpdate, MaintenanceReportResponse,
    MaintenanceCatalogueItemCreate, MaintenanceCatalogueItemUpdate, MaintenanceCatalogueItemResponse
)
from schemas.common import PaginatedResponse
from services import maintenance_service
from services.company_service import get_user_permissions

router = APIRouter()

CATALOGUE_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def has_valid_image_signature(content: bytes, content_type: str) -> bool:
    if content_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if content_type == "image/webp":
        return len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP"
    return False


def require_any_permission(db: Session, current_user: User, permissions: List[str]) -> None:
    """Require any matching resolved permission for sensitive maintenance actions."""
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


@router.get("/statistics")
async def get_maintenance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance statistics."""
    return maintenance_service.get_maintenance_statistics(db)


@router.get("/reports", response_model=PaginatedResponse[MaintenanceReportResponse])
async def list_maintenance_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    equipment_id: Optional[int] = None,
    craftsman_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all maintenance reports with optional filters."""
    skip = (page - 1) * limit
    reports = maintenance_service.get_maintenance_reports(
        db, skip=skip, limit=limit, search=search,
        equipment_id=equipment_id, craftsman_id=craftsman_id
    )
    total = maintenance_service.get_reports_count(
        db, search=search, equipment_id=equipment_id, craftsman_id=craftsman_id
    )
    
    return PaginatedResponse(
        success=True,
        data=reports,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/reports", response_model=MaintenanceReportResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_report(
    report: MaintenanceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new maintenance report."""
    return maintenance_service.create_maintenance_report(db, report)


@router.get("/reports/{report_id}", response_model=MaintenanceReportResponse)
async def get_maintenance_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance report by ID."""
    report = maintenance_service.get_maintenance_report(db, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")
    return report


@router.put("/reports/{report_id}", response_model=MaintenanceReportResponse)
async def update_maintenance_report(
    report_id: int,
    report: MaintenanceReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update maintenance report."""
    updated = maintenance_service.update_maintenance_report(db, report_id, report)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")
    return updated


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete maintenance report."""
    deleted = maintenance_service.delete_maintenance_report(db, report_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")


@router.post("/reports/{report_id}/review", response_model=MaintenanceReportResponse)
async def review_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark maintenance report as reviewed."""
    report = maintenance_service.review_maintenance_report(db, report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance report not found")
    return report


@router.get("/reports/by-work-order/{work_order_id}", response_model=List[MaintenanceReportResponse])
async def get_work_order_reports(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance reports for a work order."""
    return maintenance_service.get_work_order_reports(db, work_order_id)


@router.get("/reports/by-equipment/{equipment_id}", response_model=List[MaintenanceReportResponse])
async def get_equipment_history(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance history for an equipment."""
    return maintenance_service.get_equipment_maintenance_history(db, equipment_id)


@router.get("/reports/by-craftsman/{craftsman_id}", response_model=List[MaintenanceReportResponse])
async def get_craftsman_reports(
    craftsman_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance reports by a craftsman."""
    return maintenance_service.get_craftsman_reports(db, craftsman_id)


# ==================== PARTS AND TOOLS CATALOGUE ENDPOINTS ====================

@router.post("/catalogue/images", status_code=status.HTTP_201_CREATED)
async def upload_catalogue_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a validated spare-part or tool image."""
    require_any_permission(db, current_user, ["maintenance.catalogue.create", "maintenance.catalogue.edit"])

    extension = CATALOGUE_IMAGE_TYPES.get(image.content_type or "")
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported"
        )

    content = await image.read(settings.MAX_UPLOAD_SIZE + 1)
    await image.close()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image file is empty")
    if len(content) > settings.MAX_UPLOAD_SIZE:
        max_size_mb = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image must be no larger than {max_size_mb} MB"
        )

    if not has_valid_image_signature(content, image.content_type or ""):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File content is not a valid image")

    image_directory = Path(settings.UPLOAD_DIR) / "catalogue"
    image_directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (image_directory / filename).write_bytes(content)
    return {"image_url": f"/uploads/catalogue/{filename}"}

@router.get("/catalogue/categories", response_model=List[str])
async def list_catalogue_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get catalogue categories used for spare parts and tools."""
    require_any_permission(db, current_user, ["maintenance.catalogue.view", "maintenance.spare_parts.view", "maintenance.view"])
    return maintenance_service.get_catalogue_categories(db)


@router.get("/catalogue", response_model=PaginatedResponse[MaintenanceCatalogueItemResponse])
async def list_catalogue_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    item_type: Optional[MaintenanceCatalogueItemType] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get spare parts and tools with optional filters."""
    require_any_permission(db, current_user, ["maintenance.catalogue.view", "maintenance.spare_parts.view", "maintenance.view"])
    skip = (page - 1) * limit
    items = maintenance_service.get_catalogue_items(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        item_type=item_type,
        include_inactive=include_inactive
    )
    total = maintenance_service.get_catalogue_items_count(
        db,
        search=search,
        category=category,
        item_type=item_type,
        include_inactive=include_inactive
    )

    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=page,
        pageSize=limit,
        totalPages=(total + limit - 1) // limit
    )


@router.post("/catalogue", response_model=MaintenanceCatalogueItemResponse, status_code=status.HTTP_201_CREATED)
async def create_catalogue_item(
    item: MaintenanceCatalogueItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a spare part or tool catalogue item."""
    require_any_permission(db, current_user, ["maintenance.catalogue.create", "maintenance.spare_parts.create"])
    return maintenance_service.create_catalogue_item(db, item)


@router.get("/catalogue/{item_id}", response_model=MaintenanceCatalogueItemResponse)
async def get_catalogue_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get catalogue item by ID."""
    require_any_permission(db, current_user, ["maintenance.catalogue.view", "maintenance.spare_parts.view", "maintenance.view"])
    item = maintenance_service.get_catalogue_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")
    return item


@router.put("/catalogue/{item_id}", response_model=MaintenanceCatalogueItemResponse)
async def update_catalogue_item(
    item_id: int,
    item: MaintenanceCatalogueItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a spare part or tool catalogue item."""
    require_any_permission(db, current_user, ["maintenance.catalogue.edit", "maintenance.spare_parts.edit"])
    updated = maintenance_service.update_catalogue_item(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")
    return updated


@router.delete("/catalogue/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalogue_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deactivate a catalogue item."""
    require_any_permission(db, current_user, ["maintenance.catalogue.delete", "maintenance.spare_parts.delete"])
    deleted = maintenance_service.delete_catalogue_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")
