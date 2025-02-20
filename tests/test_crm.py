"""
Testes para o módulo CRM.
"""
import pytest
from datetime import datetime, timedelta
from src.crm.models import Client, Deal, Activity, FollowUp, ClientStatus, DealStatus
from src.crm.manager import CRMManager

@pytest.fixture
def crm_manager(tmp_path):
    """Fixture que cria um gerenciador CRM com diretório temporário."""
    return CRMManager(data_dir=str(tmp_path / "crm"))

@pytest.fixture
def sample_client():
    """Fixture que cria um cliente de exemplo."""
    return Client(
        name="Empresa Teste",
        status=ClientStatus.LEAD,
        company="Teste Inc",
        website="https://teste.com"
    )

@pytest.fixture
def sample_deal(sample_client):
    """Fixture que cria uma oportunidade de exemplo."""
    return Deal(
        client_id=sample_client.id,
        title="Projeto Teste",
        value=10000.0,
        description="Projeto teste para desenvolvimento"
    )

class TestCRMManager:
    """Testes para o CRMManager."""
    
    def test_add_client(self, crm_manager, sample_client):
        """Testa adição de cliente."""
        client = crm_manager.add_client(sample_client)
        assert client.id == sample_client.id
        assert client.name == "Empresa Teste"
        assert client.status == ClientStatus.LEAD

    def test_update_client(self, crm_manager, sample_client):
        """Testa atualização de cliente."""
        client = crm_manager.add_client(sample_client)
        updated = crm_manager.update_client(client.id, {"status": ClientStatus.ACTIVE})
        assert updated.status == ClientStatus.ACTIVE

    def test_add_deal(self, crm_manager, sample_client, sample_deal):
        """Testa adição de oportunidade."""
        crm_manager.add_client(sample_client)
        deal = crm_manager.add_deal(sample_deal)
        assert deal.id == sample_deal.id
        assert deal.value == 10000.0

    def test_update_deal_status(self, crm_manager, sample_client, sample_deal):
        """Testa atualização de status de oportunidade."""
        crm_manager.add_client(sample_client)
        deal = crm_manager.add_deal(sample_deal)
        updated = crm_manager.update_deal_status(deal.id, DealStatus.PROPOSAL_SENT)
        assert updated.status == DealStatus.PROPOSAL_SENT

    def test_add_activity(self, crm_manager, sample_client):
        """Testa adição de atividade."""
        client = crm_manager.add_client(sample_client)
        activity = Activity(
            client_id=client.id,
            type="email",
            description="Email inicial",
            created_by="test@example.com"
        )
        result = crm_manager.add_activity(activity)
        assert result.id == activity.id
        assert result.type == "email"

    def test_schedule_followup(self, crm_manager, sample_client):
        """Testa agendamento de follow-up."""
        client = crm_manager.add_client(sample_client)
        followup = FollowUp(
            client_id=client.id,
            type="call",
            description="Ligar para cliente",
            due_date=datetime.now() + timedelta(days=1)
        )
        result = crm_manager.schedule_followup(followup)
        assert result.id == followup.id
        assert result.type == "call"

    def test_get_pending_followups(self, crm_manager, sample_client):
        """Testa listagem de follow-ups pendentes."""
        client = crm_manager.add_client(sample_client)
        followup1 = FollowUp(
            client_id=client.id,
            type="call",
            description="Ligar amanhã",
            due_date=datetime.now() + timedelta(days=1)
        )
        followup2 = FollowUp(
            client_id=client.id,
            type="email",
            description="Email ontem",
            due_date=datetime.now() - timedelta(days=1),
            status="completed"
        )
        crm_manager.schedule_followup(followup1)
        crm_manager.schedule_followup(followup2)
        
        pending = crm_manager.get_pending_followups()
        assert len(pending) == 1
        assert pending[0].id == followup1.id

    def test_get_pipeline_summary(self, crm_manager, sample_client):
        """Testa resumo do pipeline."""
        client = crm_manager.add_client(sample_client)
        deal1 = Deal(
            client_id=client.id,
            title="Projeto A",
            value=10000.0,
            status=DealStatus.PROPOSAL_SENT
        )
        deal2 = Deal(
            client_id=client.id,
            title="Projeto B",
            value=20000.0,
            status=DealStatus.NEGOTIATION
        )
        crm_manager.add_deal(deal1)
        crm_manager.add_deal(deal2)
        
        summary = crm_manager.get_pipeline_summary()
        assert len(summary[DealStatus.PROPOSAL_SENT]) == 1
        assert len(summary[DealStatus.NEGOTIATION]) == 1
        assert summary[DealStatus.PROPOSAL_SENT][0]["value"] == 10000.0
        assert summary[DealStatus.NEGOTIATION][0]["value"] == 20000.0

    def test_get_sales_forecast(self, crm_manager, sample_client):
        """Testa previsão de vendas."""
        client = crm_manager.add_client(sample_client)
        deal1 = Deal(
            client_id=client.id,
            title="Projeto A",
            value=10000.0,
            status=DealStatus.PROPOSAL_SENT
        )
        deal2 = Deal(
            client_id=client.id,
            title="Projeto B",
            value=20000.0,
            status=DealStatus.WON
        )
        crm_manager.add_deal(deal1)
        crm_manager.add_deal(deal2)
        
        forecast = crm_manager.get_sales_forecast()
        assert forecast["total_pipeline"] == 30000.0
        assert forecast["won_deals"] == 20000.0
        assert forecast["deal_count"] == 2

    def test_invalid_client_id(self, crm_manager, sample_deal):
        """Testa erro ao adicionar deal com cliente inválido."""
        with pytest.raises(ValueError):
            crm_manager.add_deal(sample_deal)

    def test_invalid_deal_id(self, crm_manager):
        """Testa erro ao atualizar deal inválido."""
        with pytest.raises(ValueError):
            crm_manager.update_deal_status("invalid_id", DealStatus.WON)