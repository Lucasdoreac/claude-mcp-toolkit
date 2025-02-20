"""
Integration models and schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.api.database import Base

class Integration(Base):
    """Integration database model."""
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # crm, payment, email, calendar, etc
    provider = Column(String, nullable=False)  # hubspot, stripe, sendgrid, google, etc
    config = Column(JSON, nullable=False)
    credentials = Column(JSON, nullable=False)
    status = Column(String, default="inactive")  # inactive, active, error
    is_enabled = Column(Boolean, default=True)
    error_message = Column(Text)
    last_sync = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="integrations")
    sync_logs = relationship("IntegrationSyncLog", back_populates="integration")

class IntegrationSyncLog(Base):
    """Integration sync log database model."""
    __tablename__ = "integration_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"))
    status = Column(String, nullable=False)  # success, error
    items_processed = Column(Integer, default=0)
    items_succeeded = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    integration = relationship("Integration", back_populates="sync_logs")

class IntegrationCreate(BaseModel):
    """Schema for creating integrations."""
    name: str
    type: str
    provider: str
    config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, Any] = Field(default_factory=dict)

class IntegrationUpdate(BaseModel):
    """Schema for updating integrations."""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None

class IntegrationRead(BaseModel):
    """Schema for reading integrations."""
    id: int
    name: str
    type: str
    provider: str
    config: Dict[str, Any]
    status: str
    is_enabled: bool
    error_message: Optional[str]
    last_sync: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class IntegrationSyncLogCreate(BaseModel):
    """Schema for creating integration sync logs."""
    integration_id: int
    status: str
    items_processed: int = 0
    items_succeeded: int = 0
    items_failed: int = 0
    error_message: Optional[str] = None

class IntegrationSyncLogRead(BaseModel):
    """Schema for reading integration sync logs."""
    id: int
    integration_id: int
    status: str
    items_processed: int
    items_succeeded: int
    items_failed: int
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class IntegrationProvider(BaseModel):
    """Schema for integration provider metadata."""
    id: str
    name: str
    type: str
    description: str
    auth_type: str  # oauth2, api_key, basic
    config_schema: Dict[str, Any]
    credentials_schema: Dict[str, Any]
    features: List[str]
    docs_url: str