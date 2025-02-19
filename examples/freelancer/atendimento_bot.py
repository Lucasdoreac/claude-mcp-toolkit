"""
Bot de Atendimento Personalizado
Gerencia múltiplos canais, FAQs e encaminhamentos
Preço Referência: R$800-2000
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from openai import OpenAI
import json
import pandas as pd

class AtendimentoBot:
    """
    Bot completo para atendimento multicanal
    """
    def __init__(self):
        # APIs
        self.whatsapp_api = WhatsAppAPI(os.getenv('WA_TOKEN'))
        self.telegram_api = TelegramAPI(os.getenv('TG_TOKEN'))
        self.messenger_api = MessengerAPI(os.getenv('FB_TOKEN'))
        self.openai = OpenAI(api_key=os.getenv('OPENAI_KEY'))
        self.sheets_api = GoogleSheetsAPI(os.getenv('SHEETS_CREDENTIALS'))
        
        # Configurações
        self.load_config()
        
        # Cache
        self.context_cache = {}
        self.faqs_cache = {}
        self.analytics = {}
    
    def load_config(self):
        """
        Carrega configurações do bot
        """
        with open('config/atendimento.json', 'r') as f:
            self.config = json.load(f)
        
        self.prompts = self.config['prompts']
        self.regras = self.config['regras']
        self.horario_atendimento = self.config['horario']
        
        # Carregar FAQs
        self.load_faqs()
    
    async def load_faqs(self):
        """
        Carrega base de FAQs
        """
        faqs = await self.sheets_api.get_sheet(
            os.getenv('FAQS_SHEET_ID')
        )
        
        # Processar FAQs
        self.faqs_cache = {}
        for faq in faqs:
            self.faqs_cache[faq['pergunta']] = {
                'resposta': faq['resposta'],
                'categoria': faq['categoria'],
                'keywords': faq['keywords'].split(',')
            }
    
    async def process_message(
        self,
        message: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Processa mensagem recebida
        """
        try:
            # Registrar analytics
            self._log_message(message, platform)
            
            # Verificar horário
            if not self._check_horario():
                return await self._resposta_fora_horario(platform)
            
            # Buscar/criar contexto
            context = await self._get_context(message, platform)
            
            # Verificar tipo de atendimento
            if context['human_agent']:
                return await self._encaminhar_humano(message, context)
            
            # Processar mensagem
            resposta = await self._generate_response(message, context)
            
            # Atualizar contexto
            await self._update_context(context, message, resposta)
            
            return resposta
        
        except Exception as e:
            print(f"Erro no processamento: {str(e)}")
            return self._resposta_erro()
    
    def _log_message(self, message: Dict[str, Any], platform: str):
        """
        Registra mensagem para analytics
        """
        if platform not in self.analytics:
            self.analytics[platform] = {
                'total_messages': 0,
                'users': set(),
                'categories': {},
                'response_time': []
            }
        
        self.analytics[platform]['total_messages'] += 1
        self.analytics[platform]['users'].add(message['user_id'])
    
    def _check_horario(self) -> bool:
        """
        Verifica se está dentro do horário de atendimento
        """
        now = datetime.now()
        
        if now.weekday() in self.horario_atendimento['dias']:
            hora = now.hour
            return (
                hora >= self.horario_atendimento['inicio'] and
                hora < self.horario_atendimento['fim']
            )
        
        return False
    
    async def _get_context(
        self,
        message: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Busca ou cria contexto da conversa
        """
        context_key = f"{platform}_{message['user_id']}"
        
        if context_key not in self.context_cache:
            self.context_cache[context_key] = {
                'user_id': message['user_id'],
                'platform': platform,
                'start_time': datetime.now(),
                'messages': [],
                'human_agent': False,
                'categoria': None
            }
        
        return self.context_cache[context_key]
    
    async def _generate_response(
        self,
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera resposta para a mensagem
        """
        # Verificar FAQs
        faq_response = await self._check_faqs(message['text'])
        if faq_response:
            return {
                'type': 'text',
                'content': faq_response['resposta'],
                'categoria': faq_response['categoria']
            }
        
        # Gerar resposta com IA
        prompt = self._build_prompt(message, context)
        response = await self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.prompts['system']},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Processar resposta
        resposta = self._process_ai_response(
            response.choices[0].message.content
        )
        
        # Verificar necessidade de agente humano
        if self._needs_human_agent(message, context, resposta):
            context['human_agent'] = True
            return await self._encaminhar_humano(message, context)
        
        return resposta
    
    async def _check_faqs(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Verifica se mensagem pode ser respondida por FAQ
        """
        text = text.lower()
        
        # Buscar por correspondência exata
        for pergunta, faq in self.faqs_cache.items():
            if text == pergunta.lower():
                return faq
        
        # Buscar por keywords
        for faq in self.faqs_cache.values():
            if any(keyword in text for keyword in faq['keywords']):
                return faq
        
        return None
    
    def _build_prompt(
        self,
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Constrói prompt para IA
        """
        # Contexto da conversa
        conversation = "\n".join([
            f"{m['role']}: {m['text']}"
            for m in context['messages'][-5:]  # Últimas 5 mensagens
        ])
        
        return f"""
        Histórico:
        {conversation}
        
        Nova mensagem: {message['text']}
        
        Contexto adicional:
        - Plataforma: {context['platform']}
        - Categoria: {context['categoria']}
        - Tempo de conversa: {(datetime.now() - context['start_time']).minutes} minutos
        
        Responda de forma natural e útil.
        """
    
    def _process_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Processa resposta da IA
        """
        # Detectar tipo de resposta
        if "http" in response or "www." in response:
            return {
                'type': 'link',
                'content': response
            }
        
        if len(response) > 200:
            return {
                'type': 'long_text',
                'content': response
            }
        
        return {
            'type': 'text',
            'content': response
        }
    
    def _needs_human_agent(
        self,
        message: Dict[str, Any],
        context: Dict[str, Any],
        resposta: Dict[str, Any]
    ) -> bool:
        """
        Verifica necessidade de agente humano
        """
        # Palavras-chave de escalação
        if any(word in message['text'].lower() 
               for word in self.regras['escalation_keywords']):
            return True
        
        # Tempo de conversa
        if (datetime.now() - context['start_time']).minutes > self.regras['max_bot_time']:
            return True
        
        # Repetição de dúvidas
        if len(context['messages']) > 6:
            last_messages = context['messages'][-6:]
            similar_messages = self._check_similar_messages(last_messages)
            if similar_messages > 3:
                return True
        
        return False
    
    def _check_similar_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> int:
        """
        Verifica mensagens similares
        """
        from difflib import SequenceMatcher
        
        similar = 0
        for i in range(len(messages)):
            for j in range(i+1, len(messages)):
                similarity = SequenceMatcher(
                    None,
                    messages[i]['text'],
                    messages[j]['text']
                ).ratio()
                
                if similarity > 0.7:
                    similar += 1
        
        return similar
    
    async def _encaminhar_humano(
        self,
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Encaminha conversa para agente humano
        """
        # Notificar agente
        await self._notificar_agente(message, context)
        
        # Resposta para usuário
        return {
            'type': 'text',
            'content': self.prompts['human_handoff']
        }
    
    async def _notificar_agente(
        self,
        message: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """
        Notifica agente sobre novo atendimento
        """
        notification = f"""
        🔔 Novo Atendimento

        Plataforma: {context['platform']}
        Usuário: {message['user_id']}
        Tempo: {(datetime.now() - context['start_time']).minutes} minutos
        
        Última mensagem:
        {message['text']}
        
        Histórico:
        {self._format_history(context['messages'])}
        """
        
        # Enviar notificação
        await self._send_agent_notification(notification)
    
    def _format_history(
        self,
        messages: List[Dict[str, Any]]
    ) -> str:
        """
        Formata histórico da conversa
        """
        return "\n".join([
            f"{m['role']} ({m['timestamp'].strftime('%H:%M')}): {m['text']}"
            for m in messages
        ])
    
    async def _send_agent_notification(self, notification: str):
        """
        Envia notificação para agente
        """
        # Email
        await self.email_api.send_email(
            to_email=os.getenv('AGENT_EMAIL'),
            subject="Novo Atendimento",
            content=notification
        )
        
        # WhatsApp
        if os.getenv('AGENT_WHATSAPP'):
            await self.whatsapp_api.send_message(
                os.getenv('AGENT_WHATSAPP'),
                notification
            )
    
    async def _update_context(
        self,
        context: Dict[str, Any],
        message: Dict[str, Any],
        resposta: Dict[str, Any]
    ):
        """
        Atualiza contexto da conversa
        """
        # Adicionar mensagens
        context['messages'].append({
            'role': 'user',
            'text': message['text'],
            'timestamp': datetime.now()
        })
        
        context['messages'].append({
            'role': 'bot',
            'text': resposta['content'],
            'timestamp': datetime.now()
        })
        
        # Atualizar categoria se identificada
        if 'categoria' in resposta:
            context['categoria'] = resposta['categoria']
    
    def _resposta_fora_horario(self, platform: str) -> Dict[str, Any]:
        """
        Gera resposta para fora do horário
        """
        return {
            'type': 'text',
            'content': self.prompts['fora_horario'].format(
                inicio=self.horario_atendimento['inicio'],
                fim=self.horario_atendimento['fim']
            )
        }
    
    def _resposta_erro(self) -> Dict[str, Any]:
        """
        Gera resposta para erro
        """
        return {
            'type': 'text',
            'content': self.prompts['erro']
        }
    
    async def run_bot(self):
        """
        Executa bot de atendimento
        """
        # Inicializar handlers por plataforma
        handlers = {
            'whatsapp': self.whatsapp_api.message_handler(self.process_message),
            'telegram': self.telegram_api.message_handler(self.process_message),
            'messenger': self.messenger_api.message_handler(self.process_message)
        }
        
        # Executar handlers
        await asyncio.gather(*handlers.values())

# Exemplo de uso
async def main():
    bot = AtendimentoBot()
    
    # Iniciar bot
    await bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main())