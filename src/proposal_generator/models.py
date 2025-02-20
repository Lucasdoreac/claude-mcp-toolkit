"""
Modelos para o gerador de propostas.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ServiceItem(BaseModel):
    """Item de serviço na proposta."""
    description: str
    quantity: float = 1.0
    unit_price: float
    total: float = Field(default_factory=lambda: 0.0)
    notes: Optional[str] = None

    def calculate_total(self) -> float:
        """Calcula o total do item."""
        self.total = self.quantity * self.unit_price
        return self.total

class PaymentTerm(BaseModel):
    """Termos de pagamento."""
    description: str
    percentage: float
    due_days: int
    value: float = 0.0

class Proposal(BaseModel):
    """Modelo principal de proposta."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    client_id: str
    deal_id: Optional[str]
    title: str
    introduction: str
    scope: str
    services: List[ServiceItem]
    payment_terms: List[PaymentTerm]
    validity_days: int = 30
    terms_conditions: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = "draft"  # draft, sent, accepted, rejected
    total_value: float = 0.0

    def calculate_totals(self):
        """Calcula totais da proposta."""
        # Calcula total dos serviços
        self.total_value = sum(item.calculate_total() for item in self.services)
        
        # Atualiza valores dos termos de pagamento
        for term in self.payment_terms:
            term.value = self.total_value * (term.percentage / 100)

class ProposalTemplate(BaseModel):
    """Template de proposta."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    name: str
    description: str
    introduction_template: str
    scope_template: str
    default_services: List[ServiceItem]
    default_payment_terms: List[PaymentTerm]
    terms_conditions_template: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = []