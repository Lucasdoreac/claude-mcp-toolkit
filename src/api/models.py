"""
Modelos Pydantic para a API.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class DashboardMetrics(BaseModel):
    """Métricas principais do dashboard."""
    total_leads: int
    active_deals: int
    proposals_sent: int
    total_revenue: float

class PipelineStats(BaseModel):
    """Estatísticas do pipeline de vendas."""
    total_value: float
    closed_value: float
    conversion_rate: float
    avg_deal_size: float

class EmailStats(BaseModel):
    """Estatísticas de email marketing."""
    total_sent: int
    open_rate: float
    click_rate: float
    response_rate: float

class Deal(BaseModel):
    """Deal no pipeline de vendas."""
    id: str
    title: str
    client: str
    client_id: Optional[str]
    value: float
    status: str
    priority: Optional[str] = "medium"
    days_in_stage: Optional[int] = 0
    next_action: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    assigned_to: Optional[str]
    tags: List[str] = []

class Client(BaseModel):
    """Cliente no CRM."""
    id: str
    name: str
    company: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    status: str
    total_deals: int
    total_revenue: float
    last_contact: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    assigned_to: Optional[str]
    tags: List[str] = []

class Contact(BaseModel):
    """Contato associado a um cliente."""
    id: str
    client_id: str
    name: str
    email: EmailStr
    phone: Optional[str]
    position: Optional[str]
    is_primary: bool = False
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class Proposal(BaseModel):
    """Proposta comercial."""
    id: str
    title: str
    client_id: str
    deal_id: Optional[str]
    value: float
    status: str
    version: int = 1
    valid_until: Optional[datetime]
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]
    rejected_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class Activity(BaseModel):
    """Atividade no CRM."""
    id: str
    type: str  # email, call, meeting, note
    client_id: str
    deal_id: Optional[str]
    description: str
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]

class Dashboard(BaseModel):
    """Dados completos do dashboard."""
    metrics: DashboardMetrics
    pipeline_stats: PipelineStats
    recent_deals: List[Deal]
    email_stats: EmailStats

class DealCreate(BaseModel):
    """Dados para criar um novo deal."""
    title: str
    client_id: str
    value: float
    status: str = "new"
    priority: Optional[str]
    description: Optional[str]
    assigned_to: Optional[str]
    tags: List[str] = []

class DealUpdate(BaseModel):
    """Dados para atualizar um deal."""
    title: Optional[str]
    value: Optional[float]
    status: Optional[str]
    priority: Optional[str]
    description: Optional[str]
    assigned_to: Optional[str]
    tags: Optional[List[str]]

class ClientCreate(BaseModel):
    """Dados para criar um novo cliente."""
    name: str
    company: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    status: str = "lead"
    notes: Optional[str]
    assigned_to: Optional[str]
    tags: List[str] = []

class ClientUpdate(BaseModel):
    """Dados para atualizar um cliente."""
    name: Optional[str]
    company: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    status: Optional[str]
    notes: Optional[str]
    assigned_to: Optional[str]
    tags: Optional[List[str]]

class ProposalCreate(BaseModel):
    """Dados para criar uma nova proposta."""
    title: str
    client_id: str
    deal_id: Optional[str]
    value: float
    valid_until: Optional[datetime]
    notes: Optional[str]

class ProposalUpdate(BaseModel):
    """Dados para atualizar uma proposta."""
    title: Optional[str]
    value: Optional[float]
    status: Optional[str]
    valid_until: Optional[datetime]
    notes: Optional[str]

class ActivityCreate(BaseModel):
    """Dados para criar uma nova atividade."""
    type: str
    client_id: str
    deal_id: Optional[str]
    description: str
    scheduled_at: Optional[datetime]
    notes: Optional[str]

class ActivityUpdate(BaseModel):
    """Dados para atualizar uma atividade."""
    type: Optional[str]
    description: Optional[str]
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]