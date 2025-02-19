"""
Sistema de Gestão Financeira para Freelancers
Controla receitas, despesas, impostos e relatórios
Preço Referência: R$1000-2500
"""

[Conteúdo anterior mantido...]

    async def gerar_relatorio_mensal(self) -> str:
        """
        Gera relatório financeiro mensal
        """
        # Calcular métricas
        impostos = await self.calcular_impostos()
        previsoes = await self.gerar_previsoes()
        
        # Mês atual
        mes_atual = datetime.now().strftime('%Y-%m')
        
        report = f"""
        📊 Relatório Financeiro - {mes_atual} 📊
        
        💰 Receitas e Despesas
        • Receitas: R$ {previsoes['historico']['receitas'][mes_atual]:,.2f}
        • Despesas: R$ {previsoes['historico']['despesas'][mes_atual]:,.2f}
        • Resultado: R$ {previsoes['historico']['receitas'][mes_atual] - previsoes['historico']['despesas'][mes_atual]:,.2f}
        
        📈 Comparação com Mês Anterior
        • Receitas: {self._calcular_variacao(previsoes['historico']['receitas'], mes_atual)}%
        • Despesas: {self._calcular_variacao(previsoes['historico']['despesas'], mes_atual)}%
        
        💵 Impostos a Pagar
        """
        
        for imposto, valor in impostos['impostos_mes'][-1]['impostos'].items():
            report += f"• {imposto.upper()}: R$ {valor:,.2f}\n"
        
        report += f"Total: R$ {impostos['impostos_mes'][-1]['total']:,.2f}\n\n"
        
        report += """
        🎯 Previsão Próximos 3 Meses
        """
        
        for previsao in previsoes['previsoes']:
            report += f"""
            {previsao['mes']}:
            • Receitas: R$ {previsao['receitas']:,.2f}
            • Despesas: R$ {previsao['despesas']:,.2f}
            • Resultado: R$ {previsao['resultado']:,.2f}
            """
        
        report += "\n⚠️ Alertas e Recomendações\n"
        
        # Gerar alertas
        alertas = self._gerar_alertas(previsoes, impostos)
        for alerta in alertas:
            report += f"• {alerta}\n"
        
        return report
    
    def _calcular_variacao(
        self,
        serie: Dict[str, float],
        mes_atual: str
    ) -> float:
        """
        Calcula variação percentual
        """
        meses = sorted(serie.keys())
        if len(meses) < 2:
            return 0
        
        mes_anterior = meses[-2]
        return ((serie[mes_atual] / serie[mes_anterior]) - 1) * 100
    
    def _gerar_alertas(
        self,
        previsoes: Dict[str, Any],
        impostos: Dict[str, Any]
    ) -> List[str]:
        """
        Gera alertas e recomendações
        """
        alertas = []
        
        # Verificar tendências
        for previsao in previsoes['previsoes']:
            if previsao['resultado'] < 0:
                alertas.append(
                    f"Déficit previsto em {previsao['mes']}: R$ {abs(previsao['resultado']):,.2f}"
                )
        
        # Verificar faturamento
        if impostos['faturamento_12m'] > self.limites['faturamento'] * 0.9:
            alertas.append(
                "Próximo do limite de faturamento do Simples Nacional"
            )
        
        # Verificar margem
        ultima_margem = (
            previsoes['historico']['receitas'][max(previsoes['historico']['receitas'].keys())] -
            previsoes['historico']['despesas'][max(previsoes['historico']['despesas'].keys())]
        ) / previsoes['historico']['receitas'][max(previsoes['historico']['receitas'].keys())]
        
        if ultima_margem < 0.3:
            alertas.append(
                f"Margem atual ({ultima_margem*100:.1f}%) abaixo do ideal (30%)"
            )
        
        return alertas
    
    async def run_dashboard(self):
        """
        Executa dashboard financeiro
        """
        # Iniciar API
        await self.app.startup()
        
        while True:
            try:
                # Gerar relatório
                report = await self.gerar_relatorio_mensal()
                
                # Enviar relatório
                await self.email_api.send_email(
                    to_email=os.getenv('ADMIN_EMAIL'),
                    subject=f"Relatório Financeiro - {datetime.now().strftime('%m/%Y')}",
                    content=report
                )
                
                # Verificar limites
                await self._verificar_limites_despesas()
                
                # Aguardar próxima atualização
                await asyncio.sleep(86400)  # 24 horas
                
            except Exception as e:
                print(f"Erro no dashboard: {str(e)}")
                await asyncio.sleep(300)  # 5 minutos em caso de erro

# Exemplo de uso
async def main():
    financeiro = GestaoFinanceira()
    
    # Registrar receita
    receita = {
        'data': '2025-02-19',
        'valor': 2500.00,
        'cliente': 'Empresa XYZ',
        'servico': 'Consultoria',
        'gerar_nf': True
    }
    await financeiro.registrar_receita(receita)
    
    # Registrar despesa
    despesa = {
        'data': '2025-02-19',
        'valor': 150.00,
        'descricao': 'Assinatura Software',
        'categoria': 'Ferramentas'
    }
    await financeiro.registrar_despesa(despesa)
    
    # Iniciar dashboard
    await financeiro.run_dashboard()

if __name__ == "__main__":
    asyncio.run(main())