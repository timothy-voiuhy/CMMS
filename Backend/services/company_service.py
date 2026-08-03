from sqlalchemy.orm import Session
from typing import List, Optional
from models.company import Company, Facility, Department
from schemas.company import (
    CompanyCreate, CompanyUpdate,
    FacilityCreate, FacilityUpdate,
    DepartmentCreate, DepartmentUpdate
)


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
