"""
Template models and schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from src.api.database import Base

class Template(Base):
    """Template database model."""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # email, document, proposal
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=False, default=dict)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="templates")
    instances = relationship("TemplateInstance", back_populates="template")

class TemplateInstance(Base):
    """Template instance database model."""
    __tablename__ = "template_instances"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    content = Column(Text, nullable=False)
    variables_used = Column(JSON, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    template = relationship("Template", back_populates="instances")
    creator = relationship("User")

class TemplateCreate(BaseModel):
    """Schema for creating templates."""
    name: str
    description: Optional[str] = None
    type: str
    content: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    is_default: Optional[bool] = False

class TemplateUpdate(BaseModel):
    """Schema for updating templates."""
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class TemplateRead(BaseModel):
    """Schema for reading templates."""
    id: int
    name: str
    description: Optional[str]
    type: str
    content: str
    variables: Dict[str, Any]
    version: int
    is_active: bool
    is_default: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TemplateInstanceCreate(BaseModel):
    """Schema for creating template instances."""
    template_id: int
    variables: Dict[str, Any]

class TemplateInstanceRead(BaseModel):
    """Schema for reading template instances."""
    id: int
    template_id: int
    content: str
    variables_used: Dict[str, Any]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True