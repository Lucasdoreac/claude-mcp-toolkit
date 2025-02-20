"""
Gerador de propostas com templates e customização.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Template
import markdown
import pdfkit
from .models import Proposal, ProposalTemplate, ServiceItem, PaymentTerm

class ProposalGenerator:
    def __init__(self, data_dir: str = "data/proposals", template_dir: str = "templates/proposals"):
        """Inicializa o gerador de propostas."""
        self.data_dir = Path(data_dir)
        self.template_dir = Path(template_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Carrega dados do sistema de arquivos."""
        self.proposals: Dict[str, Proposal] = {}
        self.templates: Dict[str, ProposalTemplate] = {}

        # Carregar propostas
        proposals_file = self.data_dir / "proposals.json"
        if proposals_file.exists():
            with open(proposals_file, "r") as f:
                data = json.load(f)
                self.proposals = {k: Proposal(**v) for k, v in data.items()}

        # Carregar templates
        templates_file = self.data_dir / "templates.json"
        if templates_file.exists():
            with open(templates_file, "r") as f:
                data = json.load(f)
                self.templates = {k: ProposalTemplate(**v) for k, v in data.items()}

    def _save_data(self):
        """Salva dados no sistema de arquivos."""
        # Salvar propostas
        with open(self.data_dir / "proposals.json", "w") as f:
            data = {k: v.dict() for k, v in self.proposals.items()}
            json.dump(data, f, default=str, indent=2)

        # Salvar templates
        with open(self.data_dir / "templates.json", "w") as f:
            data = {k: v.dict() for k, v in self.templates.items()}
            json.dump(data, f, default=str, indent=2)

    def create_template(self, template: ProposalTemplate) -> ProposalTemplate:
        """Cria um novo template de proposta."""
        self.templates[template.id] = template
        self._save_data()
        return template

    def get_template(self, template_id: str) -> Optional[ProposalTemplate]:
        """Retorna um template específico."""
        return self.templates.get(template_id)

    def list_templates(self, tags: Optional[List[str]] = None) -> List[ProposalTemplate]:
        """Lista templates, opcionalmente filtrados por tags."""
        if tags:
            return [t for t in self.templates.values() if any(tag in t.tags for tag in tags)]
        return list(self.templates.values())

    def create_proposal(self, template_id: str, client_id: str, 
                       deal_id: Optional[str] = None, 
                       customizations: Optional[Dict] = None) -> Proposal:
        """Cria uma nova proposta baseada em um template."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} não encontrado")

        # Criar proposta base
        proposal = Proposal(
            client_id=client_id,
            deal_id=deal_id,
            title=customizations.get("title", "Proposta Comercial"),
            introduction=Template(template.introduction_template).render(
                customizations.get("introduction_vars", {})
            ),
            scope=Template(template.scope_template).render(
                customizations.get("scope_vars", {})
            ),
            services=[ServiceItem(**s.dict()) for s in template.default_services],
            payment_terms=[PaymentTerm(**p.dict()) for p in template.default_payment_terms],
            terms_conditions=Template(template.terms_conditions_template).render(
                customizations.get("terms_vars", {})
            )
        )

        # Aplicar customizações
        if customizations:
            if "services" in customizations:
                proposal.services = [ServiceItem(**s) for s in customizations["services"]]
            if "payment_terms" in customizations:
                proposal.payment_terms = [PaymentTerm(**p) for p in customizations["payment_terms"]]

        # Calcular totais
        proposal.calculate_totals()

        self.proposals[proposal.id] = proposal
        self._save_data()
        return proposal

    def update_proposal(self, proposal_id: str, updates: Dict) -> Proposal:
        """Atualiza uma proposta existente."""
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposta {proposal_id} não encontrada")

        proposal = self.proposals[proposal_id]
        for key, value in updates.items():
            if hasattr(proposal, key):
                setattr(proposal, key, value)

        proposal.updated_at = datetime.now()
        proposal.calculate_totals()
        
        self._save_data()
        return proposal

    def generate_markdown(self, proposal_id: str) -> str:
        """Gera versão Markdown da proposta."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposta {proposal_id} não encontrada")

        md_template = """
# {{ proposal.title }}

## Introdução
{{ proposal.introduction }}

## Escopo
{{ proposal.scope }}

## Serviços e Valores

{% for service in proposal.services %}
### {{ service.description }}
- Quantidade: {{ service.quantity }}
- Valor Unitário: R$ {{ "%.2f"|format(service.unit_price) }}
- Total: R$ {{ "%.2f"|format(service.total) }}
{% if service.notes %}
> {{ service.notes }}
{% endif %}
{% endfor %}

## Valor Total: R$ {{ "%.2f"|format(proposal.total_value) }}

## Condições de Pagamento
{% for term in proposal.payment_terms %}
- {{ term.description }}: R$ {{ "%.2f"|format(term.value) }} ({{ term.percentage }}%) - {{ term.due_days }} dias
{% endfor %}

## Termos e Condições
{{ proposal.terms_conditions }}

---
Proposta válida por {{ proposal.validity_days }} dias.
Gerada em: {{ proposal.created_at.strftime('%d/%m/%Y') }}
        """
        template = Template(md_template)
        return template.render(proposal=proposal)

    def generate_pdf(self, proposal_id: str, output_path: Optional[str] = None) -> str:
        """Gera versão PDF da proposta."""
        markdown_content = self.generate_markdown(proposal_id)
        html_content = markdown.markdown(markdown_content)
        
        if not output_path:
            output_path = self.data_dir / f"proposta_{proposal_id}.pdf"
            
        pdfkit.from_string(html_content, str(output_path))
        return str(output_path)

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Retorna uma proposta específica."""
        return self.proposals.get(proposal_id)

    def list_proposals(self, client_id: Optional[str] = None, 
                      status: Optional[str] = None) -> List[Proposal]:
        """Lista propostas, opcionalmente filtradas por cliente ou status."""
        proposals = self.proposals.values()
        
        if client_id:
            proposals = [p for p in proposals if p.client_id == client_id]
        if status:
            proposals = [p for p in proposals if p.status == status]
            
        return list(proposals)