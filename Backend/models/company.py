import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel


class Company(Base, BaseModel):
    __tablename__ = "companies"
    
    name = Column(String(200), nullable=False)
    short_name = Column(String(50), nullable=True)
    industry_type = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    tax_id = Column(String(100), nullable=True)
    
    # Contact Information
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Business Settings
    currency = Column(String(10), default="USD", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Operational Settings
    working_hours_start = Column(String(10), nullable=True)
    working_hours_end = Column(String(10), nullable=True)
    working_days = Column(String(50), nullable=True)  # JSON: ["Monday", "Tuesday", ...]
    
    # Logo and branding
    logo_url = Column(String(500), nullable=True)
    
    # System settings
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    facilities = relationship("Facility", back_populates="company")


class Facility(Base, BaseModel):
    __tablename__ = "facilities"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    name = Column(String(200), nullable=False)
    facility_type = Column(String(50), nullable=False)  # plant, warehouse, office
    facility_code = Column(String(50), unique=True, nullable=False)
    
    # Location
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    gps_coordinates = Column(String(100), nullable=True)
    
    # Contact
    phone = Column(String(20), nullable=True)
    manager_name = Column(String(100), nullable=True)
    manager_contact = Column(String(20), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="facilities")
    departments = relationship("Department", back_populates="facility")


class Department(Base, BaseModel):
    __tablename__ = "departments"
    
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    department_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Manager
    manager_name = Column(String(100), nullable=True)
    cost_center = Column(String(50), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    facility = relationship("Facility", back_populates="departments")


class Role(Base, BaseModel):
    __tablename__ = "roles"
    
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, default=1, nullable=False)  # Hierarchy level (1=lowest, higher=more senior)
    category = Column(String(50), nullable=True)  # e.g., "Operations", "Management", "Technical"
    
    # Permissions metadata (for future access control)
    permissions_json = Column(Text, nullable=True)  # JSON string for future use
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_system_role = Column(Boolean, default=False, nullable=False)  # System roles cannot be deleted
    
    # Relationships - will be used by craftsmen
    # craftsmen = relationship("Craftsman", back_populates="role")

    def get_permissions(self) -> List[str]:
        """Parse and return permissions from permissions_json."""
        if not self.permissions_json:
            return []
        try:
            data = json.loads(self.permissions_json)
            if isinstance(data, dict):
                return data.get('permissions', [])
            elif isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_permissions(
        self,
        permissions: List[str],
        template: Optional[str] = None,
        custom: bool = False
    ):
        """Set permissions JSON with metadata."""
        config = {
            "version": "1.0",
            "permissions": permissions,
            "template": template,
            "custom": custom,
            "last_modified": datetime.utcnow().isoformat()
        }
        self.permissions_json = json.dumps(config)
