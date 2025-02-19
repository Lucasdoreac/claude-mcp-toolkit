"""
Sistema de gestão para profissional autônomo
Controla agenda, pagamentos e comunicação
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import pytz

class ConsultoriaManager:
    """
    Sistema completo para profissional autônomo
    Preço Referência: R$1500-3000
    """
    def __init__(self):
        # APIs
        self.calendar_api = GoogleCalendarAPI(os.getenv('CALENDAR_CREDENTIALS'))
        self.payment_api = MercadoPagoAPI(os.getenv('MP_TOKEN'))
        self.telegram_bot = TelegramBot(os.getenv('TG_TOKEN'))
        self.email_api = SendGridAPI(os.getenv('SENDGRID_KEY'))
        
        # Configurações
        self.tz = pytz.timezone('America/Sao_Paulo')
        self.consulta_duracao = int(os.getenv('CONSULTA_DURACAO', '60'))  # minutos
        self.valor_consulta = float(os.getenv('VALOR_CONSULTA', '150.00'))
        
        # Cache
        self.agenda_cache = {}
        self.last_update = None
    
    async def update_cache(self):
        """Atualiza cache da agenda"""
        if (not self.last_update or 
            (datetime.now() - self.last_update).seconds > 300):
            start = datetime.now(self.tz)
            end = start + timedelta(days=30)
            self.agenda_cache = await self.calendar_api.get_events(start, end)
            self.last_update = datetime.now()
    
    async def find_available_slot(
        self,
        data_desejada: Optional[datetime] = None
    ) -> Dict[str, datetime]:
        """
        Encontra próximo horário disponível
        """
        await self.update_cache()
        
        # Definir período de busca
        if data_desejada:
            start = data_desejada.replace(hour=8, minute=0)
        else:
            start = datetime.now(self.tz).replace(hour=8, minute=0)
            if start.hour >= 18:
                start = start + timedelta(days=1)
        
        end = start.replace(hour=18, minute=0)
        
        # Horários ocupados
        busy_times = []
        for event in self.agenda_cache:
            if start.date() == event['start'].date():
                busy_times.append((event['start'], event['end']))
        
        # Encontrar horário livre
        current = start
        while current < end:
            slot_end = current + timedelta(minutes=self.consulta_duracao)
            
            # Verificar se horário está livre
            is_available = True
            for busy_start, busy_end in busy_times:
                if (current >= busy_start and current < busy_end) or \
                   (slot_end > busy_start and slot_end <= busy_end):
                    is_available = False
                    break
            
            if is_available:
                return {
                    'start': current,
                    'end': slot_end
                }
            
            current += timedelta(minutes=30)
        
        return None
    
    async def schedule_appointment(
        self,
        client_data: Dict[str, Any],
        data_desejada: Optional[datetime] = None
    ) -> bool:
        """
        Agenda nova consulta
        """
        try:
            # Encontrar horário
            slot = await self.find_available_slot(data_desejada)
            if not slot:
                return False
            
            # Gerar pagamento
            payment = await self.generate_payment(client_data)
            
            # Agendar
            event = await self.calendar_api.create_event(
                title=f"Consulta - {client_data['name']}",
                start=slot['start'],
                end=slot['end'],
                description=f"""
                Cliente: {client_data['name']}
                Telefone: {client_data['phone']}
                Email: {client_data['email']}
                Pagamento: {payment['id']}
                """
            )
            
            # Notificar cliente
            await self.notify_client(client_data, slot, payment)
            
            return True
        except Exception as e:
            print(f"Erro ao agendar: {str(e)}")
            return False
    
    async def generate_payment(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera link de pagamento
        """
        payment_data = {
            'description': 'Consulta',
            'amount': self.valor_consulta,
            'payment_method_id': 'pix',
            'payer': {
                'email': client_data['email'],
                'first_name': client_data['name'].split()[0],
                'last_name': ' '.join(client_data['name'].split()[1:])
            }
        }
        
        return await self.payment_api.create_payment(payment_data)
    
    async def notify_client(
        self,
        client_data: Dict[str, Any],
        slot: Dict[str, datetime],
        payment: Dict[str, Any]
    ):
        """
        Notifica cliente sobre agendamento
        """
        message = f"""
        Olá {client_data['name']}!
        
        Sua consulta foi agendada para:
        📅 {slot['start'].strftime('%d/%m/%Y')}
        ⏰ {slot['start'].strftime('%H:%M')}
        
        Para confirmar, realize o pagamento:
        💰 R$ {self.valor_consulta:.2f}
        
        PIX:
        {payment['qr_code']}
        
        Dúvidas? Entre em contato!
        """
        
        # Enviar por Telegram
        if client_data.get('telegram_id'):
            await self.telegram_bot.send_message(
                client_data['telegram_id'],
                message
            )
        
        # Enviar por email
        await self.email_api.send_email(
            to_email=client_data['email'],
            subject="Consulta Agendada",
            content=message
        )
    
    async def check_payments(self):
        """
        Verifica status dos pagamentos
        """
        # Buscar próximos agendamentos
        await self.update_cache()
        
        for event in self.agenda_cache:
            # Extrair ID do pagamento
            payment_id = event['description'].split('Pagamento: ')[-1].strip()
            
            # Verificar status
            payment = await self.payment_api.get_payment(payment_id)
            
            # Se pagamento pendente e consulta próxima
            if payment['status'] == 'pending' and \
               event['start'] - datetime.now(self.tz) < timedelta(days=1):
                # Notificar cliente
                await self.send_payment_reminder(event, payment)
    
    async def send_payment_reminder(
        self,
        event: Dict[str, Any],
        payment: Dict[str, Any]
    ):
        """
        Envia lembrete de pagamento
        """
        # Extrair dados do cliente
        description_lines = event['description'].split('\n')
        client_data = {}
        for line in description_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                client_data[key.strip()] = value.strip()
        
        message = f"""
        Olá {client_data['Cliente']}!
        
        Lembrete: sua consulta está agendada para amanhã:
        📅 {event['start'].strftime('%d/%m/%Y')}
        ⏰ {event['start'].strftime('%H:%M')}
        
        ⚠️ O pagamento ainda não foi confirmado!
        
        PIX para pagamento:
        {payment['qr_code']}
        
        Valor: R$ {self.valor_consulta:.2f}
        """
        
        # Enviar por Telegram
        if 'Telegram' in client_data:
            await self.telegram_bot.send_message(
                client_data['Telegram'],
                message
            )
        
        # Enviar por email
        await self.email_api.send_email(
            to_email=client_data['Email'],
            subject="Lembrete: Pagamento Pendente",
            content=message
        )
    
    async def generate_reports(self):
        """
        Gera relatórios de performance
        """
        await self.update_cache()
        
        # Análise de horários
        total_slots = len(self.agenda_cache)
        ocupacao = len([e for e in self.agenda_cache if e['status'] == 'confirmed'])
        taxa_ocupacao = (ocupacao / total_slots * 100) if total_slots > 0 else 0
        
        # Análise financeira
        receita = sum([
            self.valor_consulta 
            for e in self.agenda_cache 
            if e['status'] == 'confirmed'
        ])
        
        # Gerar relatório
        report = f"""
        📊 Relatório de Performance 📊
        
        Período: {datetime.now(self.tz).strftime('%d/%m/%Y')}
        
        Agenda:
        - Total de Horários: {total_slots}
        - Horários Ocupados: {ocupacao}
        - Taxa de Ocupação: {taxa_ocupacao:.1f}%
        
        Financeiro:
        - Receita Total: R$ {receita:.2f}
        - Média por Dia: R$ {(receita / 30):.2f}
        
        Top Horários:
        {self._get_top_slots()}
        """
        
        # Enviar relatório
        await self.telegram_bot.send_message(
            os.getenv('ADMIN_TELEGRAM'),
            report
        )
        
        await self.email_api.send_email(
            to_email=os.getenv('ADMIN_EMAIL'),
            subject="Relatório de Performance",
            content=report
        )
    
    def _get_top_slots(self) -> str:
        """
        Analisa horários mais populares
        """
        slot_counts = {}
        for event in self.agenda_cache:
            hour = event['start'].hour
            slot_counts[hour] = slot_counts.get(hour, 0) + 1
        
        # Ordenar por popularidade
        top_slots = sorted(
            slot_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return "\n".join([
            f"- {hour}h: {count} consultas"
            for hour, count in top_slots
        ])

# Exemplo de uso
async def main():
    manager = ConsultoriaManager()
    
    # Simular agendamento
    client = {
        'name': 'Maria Silva',
        'email': 'maria@email.com',
        'phone': '11999999999',
        'telegram_id': '123456789'
    }
    
    success = await manager.schedule_appointment(client)
    if success:
        print("Consulta agendada com sucesso!")
    
    # Verificar pagamentos
    await manager.check_payments()
    
    # Gerar relatórios
    await manager.generate_reports()

if __name__ == "__main__":
    asyncio.run(main())