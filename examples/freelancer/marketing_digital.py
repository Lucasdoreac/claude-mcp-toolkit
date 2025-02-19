"""
Sistema de Marketing Digital Automatizado
Gerencia postagens, engajamento e relatórios
Preço Referência: R$1000-2500/mês
"""

import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
from openai import OpenAI
import pandas as pd

class MarketingManager:
    """
    Sistema completo de marketing digital
    """
    def __init__(self):
        # APIs
        self.instagram_api = InstagramAPI(os.getenv('INSTAGRAM_TOKEN'))
        self.facebook_api = FacebookAPI(os.getenv('FACEBOOK_TOKEN'))
        self.linkedin_api = LinkedInAPI(os.getenv('LINKEDIN_TOKEN'))
        self.canva_api = CanvaAPI(os.getenv('CANVA_TOKEN'))
        self.analytics_api = GoogleAnalyticsAPI(os.getenv('GA_CREDENTIALS'))
        self.openai = OpenAI(api_key=os.getenv('OPENAI_KEY'))
        
        # Configurações
        self.post_frequency = int(os.getenv('POST_FREQUENCY', '3'))  # posts por semana
        self.engagement_threshold = float(os.getenv('ENGAGEMENT_THRESHOLD', '0.05'))
        
        # Cache
        self.content_cache = {}
        self.analytics_cache = {}
    
    async def generate_content(self, topic: str) -> Dict[str, Any]:
        """
        Gera conteúdo com IA
        """
        prompt = f"""
        Crie uma postagem sobre {topic} para redes sociais.
        Inclua:
        - Título chamativo
        - Texto principal
        - Hashtags relevantes
        - Sugestão de imagem
        
        Formato desejado: postagem profissional e engajante.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        
        # Processar resposta
        lines = content.split('\n')
        return {
            'title': lines[0],
            'text': '\n'.join(lines[1:-2]),
            'hashtags': lines[-2],
            'image_prompt': lines[-1]
        }
    
    async def create_image(self, prompt: str) -> str:
        """
        Cria imagem no Canva
        """
        template = await self.canva_api.get_template('social_media_post')
        design = await self.canva_api.create_design(template)
        
        # Adicionar elementos
        await self.canva_api.add_text(design, prompt['title'])
        await self.canva_api.add_image(design, prompt['image_prompt'])
        
        # Exportar
        return await self.canva_api.export_design(design)
    
    async def schedule_posts(self, content: Dict[str, Any]):
        """
        Agenda postagens nas redes sociais
        """
        # Gerar imagem
        image_url = await self.create_image(content)
        
        # Preparar cronograma
        now = datetime.now()
        schedule = [
            now + timedelta(days=1),  # Instagram
            now + timedelta(days=1, hours=2),  # Facebook
            now + timedelta(days=1, hours=4)  # LinkedIn
        ]
        
        # Agendar
        post_data = {
            'text': f"{content['title']}\n\n{content['text']}\n\n{content['hashtags']}",
            'image': image_url
        }
        
        tasks = [
            self.instagram_api.schedule_post(post_data, schedule[0]),
            self.facebook_api.schedule_post(post_data, schedule[1]),
            self.linkedin_api.schedule_post(post_data, schedule[2])
        ]
        
        return await asyncio.gather(*tasks)
    
    async def analyze_engagement(self, days: int = 30) -> Dict[str, Any]:
        """
        Analisa engajamento das postagens
        """
        # Coletar dados
        start_date = datetime.now() - timedelta(days=days)
        
        instagram_data = await self.instagram_api.get_posts(start_date)
        facebook_data = await self.facebook_api.get_posts(start_date)
        linkedin_data = await self.linkedin_api.get_posts(start_date)
        
        # Consolidar métricas
        all_posts = []
        for platform, posts in [
            ('Instagram', instagram_data),
            ('Facebook', facebook_data),
            ('LinkedIn', linkedin_data)
        ]:
            for post in posts:
                engagement = (
                    post['likes'] + post['comments'] + post['shares']
                ) / post['reach'] if post['reach'] > 0 else 0
                
                all_posts.append({
                    'platform': platform,
                    'date': post['date'],
                    'reach': post['reach'],
                    'engagement': engagement,
                    'link_clicks': post.get('link_clicks', 0)
                })
        
        df = pd.DataFrame(all_posts)
        
        return {
            'total_reach': df['reach'].sum(),
            'avg_engagement': df['engagement'].mean(),
            'best_platform': df.groupby('platform')['engagement'].mean().idxmax(),
            'best_time': df.groupby(df['date'].dt.hour)['engagement'].mean().idxmax(),
            'total_clicks': df['link_clicks'].sum(),
            'platform_performance': df.groupby('platform').agg({
                'reach': 'sum',
                'engagement': 'mean',
                'link_clicks': 'sum'
            }).to_dict()
        }
    
    async def generate_report(self) -> str:
        """
        Gera relatório de performance
        """
        # Análise de engajamento
        engagement = await self.analyze_engagement()
        
        # Analytics
        analytics = await self.analytics_api.get_metrics([
            'users',
            'sessions',
            'bounceRate',
            'goalCompletions'
        ])
        
        # Gerar relatório
        report = f"""
        📊 Relatório de Marketing Digital 📊
        
        Período: Últimos 30 dias
        
        Redes Sociais:
        - Alcance Total: {engagement['total_reach']:,}
        - Engajamento Médio: {engagement['avg_engagement']*100:.1f}%
        - Melhor Plataforma: {engagement['best_platform']}
        - Melhor Horário: {engagement['best_time']}h
        - Cliques Totais: {engagement['total_clicks']:,}
        
        Website:
        - Usuários: {analytics['users']:,}
        - Sessões: {analytics['sessions']:,}
        - Taxa de Rejeição: {analytics['bounceRate']:.1f}%
        - Conversões: {analytics['goalCompletions']:,}
        
        Performance por Plataforma:
        """
        
        for platform, metrics in engagement['platform_performance'].items():
            report += f"""
            {platform}:
            - Alcance: {metrics['reach']:,}
            - Engajamento: {metrics['engagement']*100:.1f}%
            - Cliques: {metrics['link_clicks']:,}
            """
        
        return report
    
    async def monitor_mentions(self):
        """
        Monitora menções da marca
        """
        platforms = {
            'instagram': self.instagram_api,
            'facebook': self.facebook_api,
            'linkedin': self.linkedin_api
        }
        
        mentions = []
        for platform, api in platforms.items():
            platform_mentions = await api.get_mentions()
            for mention in platform_mentions:
                sentiment = await self.analyze_sentiment(mention['text'])
                mentions.append({
                    'platform': platform,
                    'text': mention['text'],
                    'user': mention['user'],
                    'date': mention['date'],
                    'sentiment': sentiment,
                    'url': mention['url']
                })
        
        # Alertar menções negativas
        negative_mentions = [
            m for m in mentions 
            if m['sentiment'] < -0.5
        ]
        
        if negative_mentions:
            await self.alert_negative_mentions(negative_mentions)
    
    async def analyze_sentiment(self, text: str) -> float:
        """
        Analisa sentimento do texto (-1 a 1)
        """
        response = await self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of this text, return only a number between -1 (very negative) and 1 (very positive)."},
                {"role": "user", "content": text}
            ]
        )
        
        return float(response.choices[0].message.content)
    
    async def alert_negative_mentions(self, mentions: List[Dict[str, Any]]):
        """
        Alerta sobre menções negativas
        """
        message = "⚠️ Menções Negativas Detectadas ⚠️\n\n"
        
        for mention in mentions:
            message += f"""
            Plataforma: {mention['platform']}
            Usuário: {mention['user']}
            Data: {mention['date'].strftime('%d/%m/%Y %H:%M')}
            Texto: {mention['text']}
            Link: {mention['url']}
            Sentimento: {mention['sentiment']:.2f}
            
            ---
            """
        
        # Enviar alerta
        await self.send_alert(message)

# Exemplo de uso
async def main():
    manager = MarketingManager()
    
    # Gerar e agendar conteúdo
    content = await manager.generate_content("dicas de produtividade")
    await manager.schedule_posts(content)
    
    # Analisar performance
    report = await manager.generate_report()
    print(report)
    
    # Monitorar menções
    await manager.monitor_mentions()

if __name__ == "__main__":
    asyncio.run(main())