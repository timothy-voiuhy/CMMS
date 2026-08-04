from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from models.company import Company, Facility, Department, Role
from schemas.company import (
    CompanyCreate, CompanyUpdate,
    FacilityCreate, FacilityUpdate,
    DepartmentCreate, DepartmentUpdate
)
from schemas.role import RoleCreate, RoleUpdate
from models.user import User, UserRole


# ==================== COMPANY SERVICES ====================

def get_company(db: Session) -> Optional[Company]:
    """Get the company (assumes single company system)."""
    return db.query(Company).first()


def create_company(db: Session, company: CompanyCreate) -> Company:
    """Create company."""
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def update_company(db: Session, company_id: int, company: CompanyUpdate) -> Optional[Company]:
    """Update company."""
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        return None
    
    update_data = company.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_company, field, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company


# ==================== FACILITY SERVICES ====================

def get_facilities(db: Session, company_id: Optional[int] = None) -> List[Facility]:
    """Get all facilities."""
    query = db.query(Facility)
    if company_id:
        query = query.filter(Facility.company_id == company_id)
    return query.all()


def get_facility(db: Session, facility_id: int) -> Optional[Facility]:
    """Get facility by ID."""
    return db.query(Facility).filter(Facility.id == facility_id).first()


def create_facility(db: Session, facility: FacilityCreate) -> Facility:
    """Create facility."""
    db_facility = Facility(**facility.model_dump())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility


def update_facility(db: Session, facility_id: int, facility: FacilityUpdate) -> Optional[Facility]:
    """Update facility."""
    db_facility = get_facility(db, facility_id)
    if not db_facility:
        return None
    
    update_data = facility.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_facility, field, value)
    
    db.commit()
    db.refresh(db_facility)
    return db_facility


def delete_facility(db: Session, facility_id: int) -> bool:
    """Delete facility."""
    db_facility = get_facility(db, facility_id)
    if not db_facility:
        return False
    
    db.delete(db_facility)
    db.commit()
    return True


# ==================== DEPARTMENT SERVICES ====================

def get_departments(db: Session, facility_id: Optional[int] = None) -> List[Department]:
    """Get all departments."""
    query = db.query(Department)
    if facility_id:
        query = query.filter(Department.facility_id == facility_id)
    return query.all()


def get_department(db: Session, department_id: int) -> Optional[Department]:
    """Get department by ID."""
    return db.query(Department).filter(Department.id == department_id).first()


def create_department(db: Session, department: DepartmentCreate) -> Department:
    """Create department."""
    db_department = Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department


def update_department(db: Session, department_id: int, department: DepartmentUpdate) -> Optional[Department]:
    """Update department."""
    db_department = get_department(db, department_id)
    if not db_department:
        return None
    
    update_data = department.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_department, field, value)
    
    db.commit()
    db.refresh(db_department)
    return db_department


def delete_department(db: Session, department_id: int) -> bool:
    """Delete department."""
    db_department = get_department(db, department_id)
    if not db_department:
        return False
    
    db.delete(db_department)
    db.commit()
    return True


# ==================== ROLE SERVICES ====================

def get_roles(db: Session, active_only: bool = False) -> List[Role]:
    """Get all roles."""
    query = db.query(Role)
    if active_only:
        query = query.filter(Role.is_active == True)
    return query.order_by(Role.level.desc(), Role.name).all()


def get_role(db: Session, role_id: int) -> Optional[Role]:
    """Get role by ID."""
    return db.query(Role).filter(Role.id == role_id).first()


def create_role(db: Session, role: RoleCreate) -> Role:
    """Create role."""
    # Check if role name already exists
    existing = db.query(Role).filter(Role.name == role.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    db_role = Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def is_admin(user: Optional[User]) -> bool:
    if not user:
        return False
    user_role_val = user.role.value if hasattr(user.role, 'value') else str(user.role)
    return user_role_val.lower() == "admin" or user.role == UserRole.ADMIN


def update_role(db: Session, role_id: int, role: RoleUpdate, current_user: Optional[User] = None) -> Optional[Role]:
    """Update role."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # System roles can only be modified by System Administrator
    if db_role.is_system_role and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Administrators can modify system roles"
        )
    
    # Check name uniqueness if changing name
    if role.name and role.name != db_role.name:
        existing = db.query(Role).filter(Role.name == role.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
    
    update_data = role.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int, current_user: Optional[User] = None) -> bool:
    """Delete role."""
    db_role = get_role(db, role_id)
    if not db_role:
        return False
    
    # System roles can only be deleted by System Administrator
    if db_role.is_system_role and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Administrators can delete system roles"
        )
    
    # Check if role is assigned to any craftsmen
    from models.craftsman import Craftsman
    assigned_count = db.query(Craftsman).filter(Craftsman.role_id == role_id).count()
    if assigned_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role. It is assigned to {assigned_count} craftsmen."
        )
    
    db.delete(db_role)
    db.commit()
    return True


# ==================== PERMISSION SERVICES ====================

def get_role_with_permissions(db: Session, role_id: int) -> Optional[dict]:
    """Get role with parsed permissions."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    return {
        "id": db_role.id,
        "name": db_role.name,
        "description": db_role.description,
        "level": db_role.level,
        "category": db_role.category,
        "permissions_json": db_role.permissions_json,
        "is_active": db_role.is_active,
        "is_system_role": db_role.is_system_role,
        "created_at": str(db_role.created_at) if db_role.created_at else "",
        "updated_at": str(db_role.updated_at) if db_role.updated_at else "",
        "parsed_permissions": db_role.get_permissions()
    }


def update_role_permissions(
    db: Session,
    role_id: int,
    permissions: List[str],
    template: str = None,
    custom: bool = False,
    current_user: Optional[User] = None
) -> Optional[Role]:
    """Update role permissions."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # System roles can only have permissions modified by System Administrator
    if db_role.is_system_role and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Administrators can modify permissions of system roles"
        )
    
    db_role.set_permissions(permissions, template, custom)
    db.commit()
    db.refresh(db_role)
    return db_role


def create_role_from_template(
    db: Session,
    name: str,
    template_key: str,
    template_permissions: List[str],
    description: str = None,
    level: int = 1,
    category: str = None
) -> Role:
    """Create a new role from a template."""
    # Check uniqueness
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    # Create role
    db_role = Role(
        name=name,
        description=description,
        level=level,
        category=category,
        is_active=True,
        is_system_role=False
    )
    db_role.set_permissions(template_permissions, template=template_key, custom=False)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_user_permissions(db: Session, user_id: int) -> List[str]:
    """
    Resolve a user's effective permissions through the chain:
    User → Craftsman → Role → permissions_json → resolve_permissions()
    
    Admin users (role='admin') get full access regardless of craftsman/role assignment.
    """
    from models.user import User, UserRole
    from models.craftsman import Craftsman
    from core.permissions import resolve_permissions
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    # Admin users get full access
    if user.role == UserRole.ADMIN:
        return resolve_permissions(["admin.full_access"])
    
    # Find craftsman for this user
    craftsman = db.query(Craftsman).filter(Craftsman.user_id == user_id).first()
    if not craftsman or not craftsman.role_id:
        return []
    
    # Get the role
    role = get_role(db, craftsman.role_id)
    if not role or not role.is_active:
        return []
    
    # Get raw permissions and resolve with inheritance
    raw_permissions = role.get_permissions()
    return resolve_permissions(raw_permissions)

