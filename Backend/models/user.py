from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from db.base import Base
from models.base import BaseModel
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CRAFTSMAN = "craftsman"
    INVENTORY = "inventory"
    QUALITY = "quality"
    PRODUCTION = "production"
    READONLY = "readonly"


class User(Base, BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.READONLY, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Relationships
    craftsman = relationship("Craftsman", back_populates="user", uselist=False)
    work_orders_created = relationship("WorkOrder", back_populates="creator", foreign_keys="WorkOrder.created_by")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
