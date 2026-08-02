from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr


class BaseModel:
    """Base model with common fields for all tables."""
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.lower() + 's'
