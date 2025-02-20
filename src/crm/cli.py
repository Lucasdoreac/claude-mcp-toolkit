"""
Interface de linha de comando para o CRM.
"""
import click
from datetime import datetime
from typing import Optional
from .manager import CRMManager
from .models import Client, Deal, Activity, FollowUp, Contact, ClientStatus, DealStatus

@click.group()
def crm():
    """Gerenciamento de CRM para freelancers."""
    pass

# Cliente commands
@crm.group()
def client():
    """Gerenciar clientes."""
    pass

@client.command()
@click.option("--name", required=True, help="Nome do cliente")
@click.option("--status", type=click.Choice(["lead", "prospect", "active", "inactive"]), default="lead")
@click.option("--company", help="Nome da empresa")
@click.option("--website", help="Website")
@click.option("--notes", help="Notas sobre o cliente")
def add(name, status, company, website, notes):
    """Adicionar novo cliente."""
    manager = CRMManager()
    client = Client(
        name=name,
        status=status,
        company=company,
        website=website,
        notes=notes
    )
    manager.add_client(client)
    click.echo(f"Cliente {name} adicionado com ID: {client.id}")

@client.command()
@click.option("--status", type=click.Choice(["lead", "prospect", "active", "inactive"]))
def list(status):
    """Listar clientes."""
    manager = CRMManager()
    clients = manager.list_clients(status=status if status else None)
    
    if not clients:
        click.echo("Nenhum cliente encontrado")
        return
        
    for client in clients:
        click.echo(f"\nID: {client.id}")
        click.echo(f"Nome: {client.name}")
        click.echo(f"Status: {client.status}")
        click.echo(f"Empresa: {client.company or 'N/A'}")
        click.echo(f"Website: {client.website or 'N/A'}")
        click.echo("-" * 40)

# Deal commands
@crm.group()
def deal():
    """Gerenciar oportunidades."""
    pass

@deal.command()
@click.option("--client-id", required=True, help="ID do cliente")
@click.option("--title", required=True, help="Título da oportunidade")
@click.option("--value", required=True, type=float, help="Valor da oportunidade")
@click.option("--description", help="Descrição da oportunidade")
def add(client_id, title, value, description):
    """Adicionar nova oportunidade."""
    manager = CRMManager()
    deal = Deal(
        client_id=client_id,
        title=title,
        value=value,
        description=description
    )
    manager.add_deal(deal)
    click.echo(f"Oportunidade {title} adicionada com ID: {deal.id}")

@deal.command()
@click.option("--status", type=click.Choice(["new", "contact_made", "proposal_sent", "negotiation", "won", "lost"]))
def list(status):
    """Listar oportunidades."""
    manager = CRMManager()
    deals = manager.list_deals(status=status if status else None)
    
    if not deals:
        click.echo("Nenhuma oportunidade encontrada")
        return
        
    for deal in deals:
        client = manager.get_client(deal.client_id)
        click.echo(f"\nID: {deal.id}")
        click.echo(f"Cliente: {client.name}")
        click.echo(f"Título: {deal.title}")
        click.echo(f"Valor: R$ {deal.value:.2f}")
        click.echo(f"Status: {deal.status}")
        click.echo(f"Criado em: {deal.created_at.strftime('%d/%m/%Y')}")
        click.echo("-" * 40)

@deal.command()
@click.argument("deal_id")
@click.argument("status", type=click.Choice(["new", "contact_made", "proposal_sent", "negotiation", "won", "lost"]))
def update_status(deal_id, status):
    """Atualizar status de uma oportunidade."""
    manager = CRMManager()
    deal = manager.update_deal_status(deal_id, DealStatus(status))
    click.echo(f"Status da oportunidade {deal.title} atualizado para {status}")

# Activity commands
@crm.group()
def activity():
    """Gerenciar atividades."""
    pass

@activity.command()
@click.option("--client-id", required=True, help="ID do cliente")
@click.option("--deal-id", help="ID da oportunidade (opcional)")
@click.option("--type", required=True, type=click.Choice(["email", "call", "meeting", "note"]))
@click.option("--description", required=True, help="Descrição da atividade")
@click.option("--created-by", required=True, help="Responsável pela atividade")
def add(client_id, deal_id, type, description, created_by):
    """Registrar nova atividade."""
    manager = CRMManager()
    activity = Activity(
        client_id=client_id,
        deal_id=deal_id,
        type=type,
        description=description,
        created_by=created_by
    )
    manager.add_activity(activity)
    click.echo(f"Atividade registrada com ID: {activity.id}")

# Follow-up commands
@crm.group()
def followup():
    """Gerenciar follow-ups."""
    pass

@followup.command()
@click.option("--client-id", required=True, help="ID do cliente")
@click.option("--deal-id", help="ID da oportunidade (opcional)")
@click.option("--type", required=True, type=click.Choice(["email", "call", "meeting"]))
@click.option("--description", required=True, help="Descrição do follow-up")
@click.option("--due-date", required=True, help="Data de vencimento (DD/MM/YYYY)")
def schedule(client_id, deal_id, type, description, due_date):
    """Agendar novo follow-up."""
    manager = CRMManager()
    try:
        due_date = datetime.strptime(due_date, "%d/%m/%Y")
    except ValueError:
        click.echo("Formato de data inválido. Use DD/MM/YYYY")
        return
        
    followup = FollowUp(
        client_id=client_id,
        deal_id=deal_id,
        type=type,
        description=description,
        due_date=due_date
    )
    manager.schedule_followup(followup)
    click.echo(f"Follow-up agendado com ID: {followup.id}")

@followup.command()
def pending():
    """Listar follow-ups pendentes."""
    manager = CRMManager()
    followups = manager.get_pending_followups()
    
    if not followups:
        click.echo("Nenhum follow-up pendente")
        return
        
    for followup in followups:
        client = manager.get_client(followup.client_id)
        click.echo(f"\nID: {followup.id}")
        click.echo(f"Cliente: {client.name}")
        click.echo(f"Tipo: {followup.type}")
        click.echo(f"Descrição: {followup.description}")
        click.echo(f"Vencimento: {followup.due_date.strftime('%d/%m/%Y')}")
        click.echo("-" * 40)

# Pipeline command
@crm.command()
def pipeline():
    """Visualizar pipeline de vendas."""
    manager = CRMManager()
    summary = manager.get_pipeline_summary()
    forecast = manager.get_sales_forecast()
    
    click.echo("\n=== Pipeline de Vendas ===\n")
    for status, deals in summary.items():
        if deals:
            total = sum(d["value"] for d in deals)
            click.echo(f"\n{status.upper()} - Total: R$ {total:.2f}")
            for deal in deals:
                click.echo(f"- {deal['title']} ({deal['client']}) - R$ {deal['value']:.2f}")
    
    click.echo("\n=== Previsão de Vendas ===\n")
    click.echo(f"Pipeline Total: R$ {forecast['total_pipeline']:.2f}")
    click.echo(f"Previsão Ponderada: R$ {forecast['weighted_forecast']:.2f}")
    click.echo(f"Deals Fechados: R$ {forecast['won_deals']:.2f}")
    click.echo(f"Total de Oportunidades: {forecast['deal_count']}")

if __name__ == "__main__":
    crm()