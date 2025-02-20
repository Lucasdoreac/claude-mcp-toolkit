"""
Modelos para integração de email.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class EmailTemplate(BaseModel):
    """Template de email."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    name: str
    subject_template: str
    body_template: str
    type: str  # proposal, followup, notification
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = []

class EmailConfig(BaseModel):
    """Configuração de email."""
    sender_name: str
    sender_email: EmailStr
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    use_tls: bool = True
    signature: Optional[str]

class EmailMessage(BaseModel):
    """Mensagem de email."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    template_id: Optional[str]
    subject: str
    body: str
    sender_email: EmailStr
    recipient_email: EmailStr
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    attachments: List[str] = []
    status: str = "draft"  # draft, queued, sent, failed
    created_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime]
    error_message: Optional[str]

class FollowUpEmail(BaseModel):
    """Email de follow-up."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    client_id: str
    deal_id: Optional[str]
    proposal_id: Optional[str]
    template_id: str
    scheduled_date: datetime
    status: str = "pending"  # pending, sent, cancelled
    created_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime]
    message_id: Optional[str]  # ID do email enviado

class EmailQueue(BaseModel):
    """Fila de emails para envio."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    message_id: str
    retry_count: int = 0
    next_try: Optional[datetime]
    priority: int = 1  # 1 (alta) a 5 (baixa)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "queued"  # queued, processing, sent, failed