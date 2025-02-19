"""
Dashboard de Analytics para Pequenos Negócios
Analisa vendas, estoque, finanças e KPIs
Preço Referência: R$800-2000/mês
"""

[Conteúdo anterior mantido...]

        report = f"""
        📊 Dashboard Analytics - {datetime.now().strftime('%d/%m/%Y')} 📊
        
        Resumo do Dia:
        • Vendas: {summary['vendas_hoje']}
        • Receita: R$ {summary['receita_hoje']:.2f}
        • Ticket Médio: R$ {summary['ticket_medio']:.2f}
        • Saldo Atual: R$ {summary['saldo_atual']:.2f}
        
        Vendas do Mês:
        • Total: {kpis['vendas']['total_mes']}
        • Receita: R$ {kpis['vendas']['receita_mes']:.2f}
        • Crescimento: {kpis['vendas']['crescimento']:.1f}%
        
        Financeiro:
        • Lucro: R$ {kpis['financeiro']['lucro_mes']:.2f}
        • Margem: {kpis['financeiro']['margem_lucro']:.1f}%
        • Despesas Fixas: R$ {kpis['financeiro']['despesas_fixas']:.2f}
        
        Estoque:
        • Giro: {kpis['estoque']['giro']:.2f}
        • Valor Total: R$ {kpis['estoque']['valor_total']:.2f}
        • Itens Críticos: {kpis['estoque']['itens_criticos']}
        
        Produtos com Estoque Crítico:
        """
        
        for produto in inventory['produtos_criticos']:
            report += f"""
            • {produto['nome']}
              Quantidade: {produto['quantidade']}
              Mínimo: {produto['min_quantidade']}
            """
        
        report += "\nAções Recomendadas:\n"
        
        # Vendas
        if kpis['vendas']['crescimento'] < 0:
            report += "• Revisar estratégia de vendas\n"
        
        # Financeiro
        if kpis['financeiro']['margem_lucro'] < 20:
            report += "• Avaliar custos e precificação\n"
        
        # Estoque
        if kpis['estoque']['itens_criticos'] > 0:
            report += "• Realizar reposição de estoque\n"
        
        return report
    
    async def send_report(self, report: str):
        """
        Envia relatório por WhatsApp
        """
        await self.wa_api.send_message(
            os.getenv('ADMIN_PHONE'),
            report
        )
    
    async def run_dashboard(self):
        """
        Executa dashboard
        """
        while True:
            # Gerar relatório
            report = await self.generate_report()
            
            # Enviar relatório
            await self.send_report(report)
            
            # Aguardar próxima atualização
            await asyncio.sleep(3600)  # 1 hora

# Exemplo de uso
async def main():
    dashboard = AnalyticsDashboard()
    
    # Iniciar API
    await dashboard.app.startup()
    
    # Iniciar dashboard
    await dashboard.run_dashboard()

if __name__ == "__main__":
    asyncio.run(main())