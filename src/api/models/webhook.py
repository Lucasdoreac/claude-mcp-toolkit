"""
Webhook models and schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.api.database import Base

class Webhook(Base):
    """Webhook database model."""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    events = Column(JSON, nullable=False)  # List of event types to trigger webhook
    headers = Column(JSON)  # Custom headers to send
    is_active = Column(Boolean, default=True)
    secret_key = Column(String)  # For signature verification
    retry_count = Column(Integer, default=3)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="webhooks")
    deliveries = relationship("WebhookDelivery", back_populates="webhook")

class WebhookDelivery(Base):
    """Webhook delivery attempt database model."""
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"))
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    response_status = Column(Integer)
    response_body = Column(Text)
    error_message = Column(Text)
    attempt_count = Column(Integer, default=1)
    is_success = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")

class WebhookCreate(BaseModel):
    """Schema for creating webhooks."""
    name: str
    url: HttpUrl
    description: Optional[str] = None
    events: List[str]
    headers: Optional[Dict[str, str]] = None
    secret_key: Optional[str] = None
    retry_count: Optional[int] = 3

class WebhookUpdate(BaseModel):
    """Schema for updating webhooks."""
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    events: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    secret_key: Optional[str] = None
    retry_count: Optional[int] = None

class WebhookRead(BaseModel):
    """Schema for reading webhooks."""
    id: int
    name: str
    url: str
    description: Optional[str]
    events: List[str]
    headers: Optional[Dict[str, str]]
    is_active: bool
    retry_count: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class WebhookDeliveryRead(BaseModel):
    """Schema for reading webhook deliveries."""
    id: int
    webhook_id: int
    event_type: str
    payload: Dict[str, Any]
    response_status: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    attempt_count: int
    is_success: bool
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class WebhookEvent(BaseModel):
    """Schema for webhook event data."""
    event_type: str
    payload: Dict[str, Any]