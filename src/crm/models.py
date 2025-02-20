"""
Modelos de dados para o CRM.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class ClientStatus(str, Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"

class DealStatus(str, Enum):
    NEW = "new"
    CONTACT_MADE = "contact_made"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"

class Contact(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]
    position: Optional[str]
    notes: Optional[str]

class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    name: str
    status: ClientStatus = ClientStatus.LEAD
    company: Optional[str]
    contacts: List[Contact] = []
    website: Optional[str]
    address: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = []
    notes: Optional[str]

class Deal(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    client_id: str
    title: str
    value: float
    status: DealStatus = DealStatus.NEW
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expected_close_date: Optional[datetime]
    actual_close_date: Optional[datetime]
    description: Optional[str]
    notes: Optional[str]
    
class Activity(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    client_id: str
    deal_id: Optional[str]
    type: str  # email, call, meeting, note
    description: str
    date: datetime = Field(default_factory=datetime.now)
    created_by: str
    notes: Optional[str]

class FollowUp(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    client_id: str
    deal_id: Optional[str]
    due_date: datetime
    status: str = "pending"  # pending, completed, cancelled
    type: str  # email, call, meeting
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime]
    notes: Optional[str]