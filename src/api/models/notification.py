"""
Notification models and schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.api.database import Base

class Notification(Base):
    """Notification database model."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # email, in_app, push
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    delivered_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class NotificationCreate(BaseModel):
    """Schema for creating notifications."""
    user_id: int
    type: str
    title: str
    content: str

class NotificationUpdate(BaseModel):
    """Schema for updating notifications."""
    read: Optional[bool] = None
    delivered_at: Optional[datetime] = None

class NotificationRead(BaseModel):
    """Schema for reading notifications."""
    id: int
    user_id: int
    type: str
    title: str
    content: str
    read: bool
    created_at: datetime
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True