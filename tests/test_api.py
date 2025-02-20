"""
Testes para a API.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.api.main import app
from src.api.models import (
    Deal, Client, Proposal, 
    DealCreate, ClientCreate, ProposalCreate
)

client = TestClient(app)

def test_get_dashboard():
    """Testa rota do dashboard."""
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    
    # Verifica estrutura da resposta
    assert "metrics" in data
    assert "pipeline_stats" in data
    assert "recent_deals" in data
    assert "email_stats" in data
    
    # Verifica métricas
    metrics = data["metrics"]
    assert isinstance(metrics["total_leads"], int)
    assert isinstance(metrics["active_deals"], int)
    assert isinstance(metrics["proposals_sent"], int)
    assert isinstance(metrics["total_revenue"], (int, float))

def test_list_deals():
    """Testa listagem de deals."""
    response = client.get("/api/deals")
    assert response.status_code == 200
    deals = response.json()
    
    assert isinstance(deals, list)
    if deals:
        deal = deals[0]
        assert "id" in deal
        assert "title" in deal
        assert "value" in deal
        assert "status" in deal

def test_list_deals_with_filters():
    """Testa listagem de deals com filtros."""
    # Teste filtro por status
    response = client.get("/api/deals?status=proposal_sent")
    assert response.status_code == 200
    deals = response.json()
    assert all(d["status"] == "proposal_sent" for d in deals)
    
    # Teste filtro por cliente
    response = client.get("/api/deals?client_id=1")
    assert response.status_code == 200
    deals = response.json()
    assert all(d["client_id"] == "1" for d in deals)

def test_get_deal():
    """Testa obtenção de deal específico."""
    # Deal existente
    response = client.get("/api/deals/1")
    assert response.status_code == 200
    deal = response.json()
    assert deal["id"] == "1"
    
    # Deal não existente
    response = client.get("/api/deals/999")
    assert response.status_code == 404

def test_update_deal_status():
    """Testa atualização de status do deal."""
    # Status válido
    response = client.post("/api/deals/1/status?status=negotiation")
    assert response.status_code == 200
    
    # Status inválido
    response = client.post("/api/deals/1/status?status=invalid")
    assert response.status_code == 400

def test_list_clients():
    """Testa listagem de clientes."""
    response = client.get("/api/clients")
    assert response.status_code == 200
    clients = response.json()
    
    assert isinstance(clients, list)
    if clients:
        client = clients[0]
        assert "id" in client
        assert "name" in client
        assert "status" in client
        assert "total_deals" in client

def test_list_clients_with_filters():
    """Testa listagem de clientes com filtros."""
    # Teste filtro por status
    response = client.get("/api/clients?status=active")
    assert response.status_code == 200
    clients = response.json()
    assert all(c["status"] == "active" for c in clients)

def test_get_client():
    """Testa obtenção de cliente específico."""
    # Cliente existente
    response = client.get("/api/clients/1")
    assert response.status_code == 200
    client = response.json()
    assert client["id"] == "1"
    
    # Cliente não existente
    response = client.get("/api/clients/999")
    assert response.status_code == 404

def test_list_proposals():
    """Testa listagem de propostas."""
    response = client.get("/api/proposals")
    assert response.status_code == 200
    proposals = response.json()
    
    assert isinstance(proposals, list)
    if proposals:
        proposal = proposals[0]
        assert "id" in proposal
        assert "title" in proposal
        assert "client_id" in proposal
        assert "value" in proposal
        assert "status" in proposal

def test_list_proposals_with_filters():
    """Testa listagem de propostas com filtros."""
    # Teste filtro por status
    response = client.get("/api/proposals?status=sent")
    assert response.status_code == 200
    proposals = response.json()
    assert all(p["status"] == "sent" for p in proposals)
    
    # Teste filtro por cliente
    response = client.get("/api/proposals?client_id=1")
    assert response.status_code == 200
    proposals = response.json()
    assert all(p["client_id"] == "1" for p in proposals)

def test_get_proposal():
    """Testa obtenção de proposta específica."""
    # Proposta existente
    response = client.get("/api/proposals/1")
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["id"] == "1"
    
    # Proposta não existente
    response = client.get("/api/proposals/999")
    assert response.status_code == 404

# Fixtures para testes
@pytest.fixture
def sample_deal():
    """Retorna um deal de exemplo."""
    return DealCreate(
        title="Website E-commerce",
        client_id="1",
        value=28000,
        status="new",
        priority="high",
        description="Desenvolvimento de website e-commerce"
    )

@pytest.fixture
def sample_client():
    """Retorna um cliente de exemplo."""
    return ClientCreate(
        name="Loja XYZ",
        company="XYZ Comércio LTDA",
        email="contato@xyz.com",
        phone="11999999999",
        status="lead",
        notes="Cliente interessado em e-commerce"
    )

@pytest.fixture
def sample_proposal():
    """Retorna uma proposta de exemplo."""
    return ProposalCreate(
        title="Website E-commerce - Proposta Comercial",
        client_id="1",
        deal_id="1",
        value=28000,
        valid_until=datetime.now() + timedelta(days=30),
        notes="Proposta inicial para desenvolvimento de e-commerce"
    )