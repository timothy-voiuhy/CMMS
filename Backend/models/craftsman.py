from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel

# Association table for craftsman skills (many-to-many)
craftsman_skills = Table(
    'craftsman_skills',
    Base.metadata,
    Column('craftsman_id', Integer, ForeignKey('craftsmen.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

# Association table for equipment operators (many-to-many)
# Defined here to avoid circular imports
equipment_operators = Table(
    'equipment_operators',
    Base.metadata,
    Column('equipment_id', Integer, ForeignKey('equipment.id'), primary_key=True),
    Column('craftsman_id', Integer, ForeignKey('craftsmen.id'), primary_key=True)
)


class Skill(Base, BaseModel):
    __tablename__ = "skills"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    
    # Relationships
    craftsmen = relationship("Craftsman", secondary=craftsman_skills, back_populates="skills")


class Craftsman(Base, BaseModel):
    __tablename__ = "craftsmen"
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    hire_date = Column(String(20), nullable=True)
    certification_level = Column(String(50), nullable=True)
    hourly_rate = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="craftsman")
    skills = relationship("Skill", secondary=craftsman_skills, back_populates="craftsmen")
    work_orders = relationship("WorkOrder", back_populates="craftsman", foreign_keys="WorkOrder.assigned_to")
    maintenance_reports = relationship("MaintenanceReport", back_populates="craftsman")
    operated_equipment = relationship("Equipment", secondary=equipment_operators, back_populates="operators")
