from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.base import Base
from models.base import BaseModel


class Notification(Base, BaseModel):
    """An in-app notification belonging to one user."""

    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)
    read = Column(Boolean, default=False, nullable=False, index=True)

    user = relationship("User", back_populates="notifications")
