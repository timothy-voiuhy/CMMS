from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ==================== COMPANY SCHEMAS ====================

class CompanyBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    industry_type: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    currency: str = "USD"
    timezone: str = "UTC"
    language: str = "en"
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    working_days: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    industry_type: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    working_days: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== FACILITY SCHEMAS ====================

class FacilityBase(BaseModel):
    name: str
    facility_type: str
    facility_code: str
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    gps_coordinates: Optional[str] = None
    phone: Optional[str] = None
    manager_name: Optional[str] = None
    manager_contact: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class FacilityCreate(FacilityBase):
    company_id: int


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    facility_type: Optional[str] = None
    facility_code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    gps_coordinates: Optional[str] = None
    phone: Optional[str] = None
    manager_name: Optional[str] = None
    manager_contact: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class FacilityResponse(FacilityBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== DEPARTMENT SCHEMAS ====================

class DepartmentBase(BaseModel):
    name: str
    department_code: str
    description: Optional[str] = None
    manager_name: Optional[str] = None
    cost_center: Optional[str] = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    facility_id: int


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    department_code: Optional[str] = None
    description: Optional[str] = None
    manager_name: Optional[str] = None
    cost_center: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: int
    facility_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
