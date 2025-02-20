"""
Gerenciador principal do CRM.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from .models import Client, Deal, Activity, FollowUp, Contact, ClientStatus, DealStatus

class CRMManager:
    def __init__(self, data_dir: str = "data/crm"):
        """Inicializa o gerenciador CRM."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Carrega dados do sistema de arquivos."""
        self.clients: Dict[str, Client] = {}
        self.deals: Dict[str, Deal] = {}
        self.activities: Dict[str, Activity] = {}
        self.followups: Dict[str, FollowUp] = {}

        # Carregar clientes
        clients_file = self.data_dir / "clients.json"
        if clients_file.exists():
            with open(clients_file, "r") as f:
                data = json.load(f)
                self.clients = {k: Client(**v) for k, v in data.items()}

        # Carregar deals
        deals_file = self.data_dir / "deals.json"
        if deals_file.exists():
            with open(deals_file, "r") as f:
                data = json.load(f)
                self.deals = {k: Deal(**v) for k, v in data.items()}

    def _save_data(self):
        """Salva dados no sistema de arquivos."""
        # Salvar clientes
        with open(self.data_dir / "clients.json", "w") as f:
            data = {k: v.dict() for k, v in self.clients.items()}
            json.dump(data, f, default=str, indent=2)

        # Salvar deals
        with open(self.data_dir / "deals.json", "w") as f:
            data = {k: v.dict() for k, v in self.deals.items()}
            json.dump(data, f, default=str, indent=2)

    # Operações com Clientes
    def add_client(self, client: Client) -> Client:
        """Adiciona um novo cliente."""
        self.clients[client.id] = client
        self._save_data()
        return client

    def update_client(self, client_id: str, updates: dict) -> Client:
        """Atualiza dados de um cliente."""
        if client_id not in self.clients:
            raise ValueError(f"Cliente {client_id} não encontrado")
        
        client = self.clients[client_id]
        updated_data = client.dict()
        updated_data.update(updates)
        updated_data["updated_at"] = datetime.now()
        
        self.clients[client_id] = Client(**updated_data)
        self._save_data()
        return self.clients[client_id]

    def get_client(self, client_id: str) -> Optional[Client]:
        """Retorna um cliente específico."""
        return self.clients.get(client_id)

    def list_clients(self, status: Optional[ClientStatus] = None) -> List[Client]:
        """Lista todos os clientes, opcionalmente filtrados por status."""
        if status:
            return [c for c in self.clients.values() if c.status == status]
        return list(self.clients.values())

    # Operações com Deals
    def add_deal(self, deal: Deal) -> Deal:
        """Adiciona uma nova oportunidade."""
        if deal.client_id not in self.clients:
            raise ValueError(f"Cliente {deal.client_id} não encontrado")
        
        self.deals[deal.id] = deal
        self._save_data()
        return deal

    def update_deal_status(self, deal_id: str, status: DealStatus) -> Deal:
        """Atualiza o status de uma oportunidade."""
        if deal_id not in self.deals:
            raise ValueError(f"Deal {deal_id} não encontrada")
        
        deal = self.deals[deal_id]
        deal.status = status
        deal.updated_at = datetime.now()
        
        if status == DealStatus.WON:
            deal.actual_close_date = datetime.now()
        
        self._save_data()
        return deal

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Retorna uma oportunidade específica."""
        return self.deals.get(deal_id)

    def list_deals(self, status: Optional[DealStatus] = None) -> List[Deal]:
        """Lista todas as oportunidades, opcionalmente filtradas por status."""
        if status:
            return [d for d in self.deals.values() if d.status == status]
        return list(self.deals.values())

    # Atividades e Follow-ups
    def add_activity(self, activity: Activity):
        """Registra uma nova atividade."""
        if activity.client_id not in self.clients:
            raise ValueError(f"Cliente {activity.client_id} não encontrado")
        
        if activity.deal_id and activity.deal_id not in self.deals:
            raise ValueError(f"Deal {activity.deal_id} não encontrada")
        
        self.activities[activity.id] = activity
        self._save_data()
        return activity

    def schedule_followup(self, followup: FollowUp):
        """Agenda um novo follow-up."""
        if followup.client_id not in self.clients:
            raise ValueError(f"Cliente {followup.client_id} não encontrado")
        
        if followup.deal_id and followup.deal_id not in self.deals:
            raise ValueError(f"Deal {followup.deal_id} não encontrada")
        
        self.followups[followup.id] = followup
        self._save_data()
        return followup

    def get_pending_followups(self) -> List[FollowUp]:
        """Retorna todos os follow-ups pendentes."""
        now = datetime.now()
        return [
            f for f in self.followups.values()
            if f.status == "pending" and f.due_date > now
        ]

    # Pipeline e Reports
    def get_pipeline_summary(self) -> Dict:
        """Retorna um resumo do pipeline de vendas."""
        summary = {status: [] for status in DealStatus}
        
        for deal in self.deals.values():
            summary[deal.status].append({
                "id": deal.id,
                "title": deal.title,
                "value": deal.value,
                "client": self.clients[deal.client_id].name
            })
        
        return summary

    def get_sales_forecast(self) -> Dict:
        """Calcula previsão de vendas."""
        forecast = {
            "total_pipeline": sum(d.value for d in self.deals.values() if d.status != DealStatus.LOST),
            "weighted_forecast": sum(
                d.value * 0.8 if d.status == DealStatus.NEGOTIATION else
                d.value * 0.5 if d.status == DealStatus.PROPOSAL_SENT else
                d.value * 0.2
                for d in self.deals.values()
                if d.status not in [DealStatus.WON, DealStatus.LOST]
            ),
            "won_deals": sum(d.value for d in self.deals.values() if d.status == DealStatus.WON),
            "deal_count": len(self.deals)
        }
        return forecast