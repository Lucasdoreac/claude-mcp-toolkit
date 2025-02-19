"""
Sistema de automação para pequena loja
Integra vendas online, estoque e notificações
"""

import os
from typing import Dict, Any, List
from datetime import datetime
import asyncio
import pandas as pd

class LojaManager:
    """
    Sistema completo para gestão de loja
    Preço Referência: R$2000-3500
    """
    def __init__(self):
        # Configurar APIs
        self.ml_api = MercadoLivreAPI(os.getenv('ML_TOKEN'))
        self.sheets_api = GoogleSheetsAPI(os.getenv('SHEETS_CREDENTIALS'))
        self.wa_api = WhatsAppAPI(os.getenv('WA_TOKEN'))
        
        # Configurar planilhas
        self.estoque_sheet = os.getenv('ESTOQUE_SHEET_ID')
        self.vendas_sheet = os.getenv('VENDAS_SHEET_ID')
        
        # Cache local
        self.estoque_cache = {}
        self.last_update = None
    
    async def update_cache(self):
        """Atualiza cache do estoque"""
        if (not self.last_update or 
            (datetime.now() - self.last_update).seconds > 300):
            self.estoque_cache = await self.sheets_api.get_sheet(self.estoque_sheet)
            self.last_update = datetime.now()
    
    async def process_sale(self, sale_data: Dict[str, Any]):
        """Processa nova venda"""
        try:
            # Atualizar estoque
            await self.update_inventory(sale_data['items'])
            
            # Notificar cliente
            await self.notify_customer(sale_data['customer'])
            
            # Registrar venda
            await self.register_sale(sale_data)
            
            # Verificar níveis baixos
            await self.check_low_stock()
            
            return True
        except Exception as e:
            print(f"Erro ao processar venda: {str(e)}")
            return False
    
    async def update_inventory(self, items: List[Dict[str, Any]]):
        """Atualiza estoque após venda"""
        await self.update_cache()
        
        updates = []
        for item in items:
            sku = item['sku']
            if sku in self.estoque_cache:
                new_qty = self.estoque_cache[sku]['quantity'] - item['quantity']
                updates.append({
                    'sku': sku,
                    'quantity': new_qty
                })
        
        if updates:
            await self.sheets_api.batch_update(self.estoque_sheet, updates)
    
    async def notify_customer(self, customer: Dict[str, Any]):
        """Envia notificação ao cliente"""
        message = f"""
        Olá {customer['name']}!
        
        Recebemos seu pedido #{customer['order_id']}.
        Prazo de envio: 2-3 dias úteis.
        
        Agradecemos a preferência!
        """
        
        await self.wa_api.send_message(
            customer['phone'],
            message
        )
    
    async def register_sale(self, sale_data: Dict[str, Any]):
        """Registra venda na planilha"""
        sale_record = {
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pedido': sale_data['order_id'],
            'cliente': sale_data['customer']['name'],
            'valor': sum(item['price'] * item['quantity'] for item in sale_data['items']),
            'itens': len(sale_data['items'])
        }
        
        await self.sheets_api.append_row(self.vendas_sheet, sale_record)
    
    async def check_low_stock(self):
        """Verifica itens com estoque baixo"""
        await self.update_cache()
        
        low_stock = []
        for sku, item in self.estoque_cache.items():
            if item['quantity'] <= item.get('min_quantity', 5):
                low_stock.append({
                    'sku': sku,
                    'name': item['name'],
                    'current': item['quantity'],
                    'min': item.get('min_quantity', 5)
                })
        
        if low_stock:
            await self.notify_low_stock(low_stock)
    
    async def notify_low_stock(self, items: List[Dict[str, Any]]):
        """Notifica sobre estoque baixo"""
        message = "⚠️ Alerta de Estoque Baixo ⚠️\n\n"
        for item in items:
            message += f"• {item['name']}\n"
            message += f"  Atual: {item['current']} | Mínimo: {item['min']}\n"
        
        # Notificar no WhatsApp
        await self.wa_api.send_message(
            os.getenv('ADMIN_PHONE'),
            message
        )
    
    async def generate_reports(self):
        """Gera relatórios diários"""
        # Buscar dados
        vendas = await self.sheets_api.get_sheet(self.vendas_sheet)
        estoque = await self.sheets_api.get_sheet(self.estoque_sheet)
        
        # Converter para DataFrame
        df_vendas = pd.DataFrame(vendas)
        df_estoque = pd.DataFrame(estoque)
        
        # Análises
        report = {
            'vendas_dia': df_vendas[df_vendas['data'].dt.date == datetime.now().date()]['valor'].sum(),
            'total_pedidos': len(df_vendas),
            'ticket_medio': df_vendas['valor'].mean(),
            'itens_criticos': len(df_estoque[df_estoque['quantity'] <= df_estoque['min_quantity']])
        }
        
        # Gerar relatório
        message = "📊 Relatório Diário 📊\n\n"
        message += f"Vendas Hoje: R$ {report['vendas_dia']:.2f}\n"
        message += f"Total Pedidos: {report['total_pedidos']}\n"
        message += f"Ticket Médio: R$ {report['ticket_medio']:.2f}\n"
        message += f"Itens Críticos: {report['itens_criticos']}\n"
        
        # Enviar relatório
        await self.wa_api.send_message(
            os.getenv('ADMIN_PHONE'),
            message
        )

# Exemplo de uso
async def main():
    loja = LojaManager()
    
    # Simular venda
    sale_data = {
        'order_id': 'PED123',
        'customer': {
            'name': 'João Silva',
            'phone': '5511999999999'
        },
        'items': [
            {
                'sku': 'PRD001',
                'quantity': 2,
                'price': 29.90
            }
        ]
    }
    
    # Processar venda
    success = await loja.process_sale(sale_data)
    if success:
        print("Venda processada com sucesso!")
    
    # Gerar relatório
    await loja.generate_reports()

if __name__ == "__main__":
    asyncio.run(main())