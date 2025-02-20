"""
SQLAlchemy models for database tables.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.api.database import Base

class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    deals = relationship("Deal", back_populates="owner")
    proposals = relationship("Proposal", back_populates="owner")

class Client(Base):
    """Client model."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company = Column(String)
    email = Column(String)
    phone = Column(String)
    status = Column(String)  # lead, active, inactive
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    deals = relationship("Deal", back_populates="client")
    proposals = relationship("Proposal", back_populates="client")

class Deal(Base):
    """Deal model."""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    value = Column(Float)
    status = Column(String)  # new, contacted, proposal_sent, negotiation, closed_won, closed_lost
    priority = Column(String)  # low, medium, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign keys
    client_id = Column(Integer, ForeignKey("clients.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    client = relationship("Client", back_populates="deals")
    owner = relationship("User", back_populates="deals")
    proposals = relationship("Proposal", back_populates="deal")

class Proposal(Base):
    """Proposal model."""
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    value = Column(Float)
    notes = Column(Text)
    valid_until = Column(DateTime(timezone=True))
    status = Column(String)  # draft, sent, accepted, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign keys
    client_id = Column(Integer, ForeignKey("clients.id"))
    deal_id = Column(Integer, ForeignKey("deals.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    client = relationship("Client", back_populates="proposals")
    deal = relationship("Deal", back_populates="proposals")
    owner = relationship("User", back_populates="proposals")