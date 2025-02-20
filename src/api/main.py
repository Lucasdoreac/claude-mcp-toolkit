"""
API principal para o Dashboard.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta

from .models import (
    Dashboard, DashboardMetrics, PipelineStats,
    Deal, Client, Proposal, EmailStats
)

app = FastAPI(
    title="Claude MCP Toolkit API",
    description="API Backend para o Dashboard do Claude MCP Toolkit",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configurar para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas do Dashboard
@app.get("/api/dashboard", response_model=Dashboard)
async def get_dashboard():
    """Retorna dados do dashboard."""
    # TODO: Integrar com banco de dados
    return Dashboard(
        metrics=DashboardMetrics(
            total_leads=124,
            active_deals=15,
            proposals_sent=45,
            total_revenue=157000
        ),
        pipeline_stats=PipelineStats(
            total_value=343000,
            closed_value=85000,
            conversion_rate=45,
            avg_deal_size=28000
        ),
        recent_deals=[
            Deal(
                id="1",
                title="Website E-commerce",
                client="Loja XYZ",
                value=28000,
                status="proposal_sent",
                created_at=datetime.now() - timedelta(days=2)
            ),
            Deal(
                id="2",
                title="Sistema ERP",
                client="Empresa ABC",
                value=45000,
                status="negotiation",
                created_at=datetime.now() - timedelta(days=5)
            )
        ],
        email_stats=EmailStats(
            total_sent=156,
            open_rate=45.2,
            click_rate=12.8,
            response_rate=8.5
        )
    )

# Rotas de Deals
@app.get("/api/deals", response_model=List[Deal])
async def list_deals(
    status: Optional[str] = None,
    client_id: Optional[str] = None
):
    """Lista deals com filtros opcionais."""
    # TODO: Implementar filtros e banco de dados
    deals = [
        Deal(
            id="1",
            title="Website E-commerce",
            client="Loja XYZ",
            value=28000,
            status="proposal_sent",
            created_at=datetime.now() - timedelta(days=2)
        ),
        Deal(
            id="2",
            title="Sistema ERP",
            client="Empresa ABC",
            value=45000,
            status="negotiation",
            created_at=datetime.now() - timedelta(days=5)
        )
    ]
    
    if status:
        deals = [d for d in deals if d.status == status]
    if client_id:
        deals = [d for d in deals if d.client_id == client_id]
        
    return deals

@app.get("/api/deals/{deal_id}", response_model=Deal)
async def get_deal(deal_id: str):
    """Retorna detalhes de um deal específico."""
    # TODO: Integrar com banco de dados
    if deal_id != "1":
        raise HTTPException(status_code=404, detail="Deal não encontrado")
        
    return Deal(
        id="1",
        title="Website E-commerce",
        client="Loja XYZ",
        value=28000,
        status="proposal_sent",
        created_at=datetime.now() - timedelta(days=2)
    )

@app.post("/api/deals/{deal_id}/status")
async def update_deal_status(deal_id: str, status: str):
    """Atualiza o status de um deal."""
    # TODO: Implementar atualização no banco de dados
    valid_statuses = ["new", "contact_made", "proposal_sent", "negotiation", "won", "lost"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Status inválido")
        
    return {"message": "Status atualizado com sucesso"}

# Rotas de Clientes
@app.get("/api/clients", response_model=List[Client])
async def list_clients(status: Optional[str] = None):
    """Lista clientes com filtros opcionais."""
    # TODO: Implementar filtros e banco de dados
    clients = [
        Client(
            id="1",
            name="Loja XYZ",
            status="active",
            total_deals=2,
            total_revenue=28000,
            created_at=datetime.now() - timedelta(days=30)
        ),
        Client(
            id="2",
            name="Empresa ABC",
            status="lead",
            total_deals=1,
            total_revenue=0,
            created_at=datetime.now() - timedelta(days=15)
        )
    ]
    
    if status:
        clients = [c for c in clients if c.status == status]
        
    return clients

@app.get("/api/clients/{client_id}", response_model=Client)
async def get_client(client_id: str):
    """Retorna detalhes de um cliente específico."""
    # TODO: Integrar com banco de dados
    if client_id != "1":
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
    return Client(
        id="1",
        name="Loja XYZ",
        status="active",
        total_deals=2,
        total_revenue=28000,
        created_at=datetime.now() - timedelta(days=30)
    )

# Rotas de Propostas
@app.get("/api/proposals", response_model=List[Proposal])
async def list_proposals(
    status: Optional[str] = None,
    client_id: Optional[str] = None
):
    """Lista propostas com filtros opcionais."""
    # TODO: Implementar filtros e banco de dados
    proposals = [
        Proposal(
            id="1",
            title="Website E-commerce - Proposta Comercial",
            client_id="1",
            deal_id="1",
            value=28000,
            status="sent",
            created_at=datetime.now() - timedelta(days=2)
        ),
        Proposal(
            id="2",
            title="Sistema ERP - Proposta Inicial",
            client_id="2", 
            deal_id="2",
            value=45000,
            status="draft",
            created_at=datetime.now() - timedelta(days=1)
        )
    ]
    
    if status:
        proposals = [p for p in proposals if p.status == status]
    if client_id:
        proposals = [p for p in proposals if p.client_id == client_id]
        
    return proposals

@app.get("/api/proposals/{proposal_id}", response_model=Proposal)
async def get_proposal(proposal_id: str):
    """Retorna detalhes de uma proposta específica."""
    # TODO: Integrar com banco de dados
    if proposal_id != "1":
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
        
    return Proposal(
        id="1",
        title="Website E-commerce - Proposta Comercial",
        client_id="1",
        deal_id="1",
        value=28000,
        status="sent",
        created_at=datetime.now() - timedelta(days=2)
    )