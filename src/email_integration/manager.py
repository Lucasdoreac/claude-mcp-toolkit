"""
Gerenciador de integração de email.
"""
import json
import smtplib
import threading
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Template

from .models import (
    EmailTemplate, EmailConfig, EmailMessage, 
    FollowUpEmail, EmailQueue
)

class EmailManager:
    def __init__(self, data_dir: str = "data/email", config: Optional[EmailConfig] = None):
        """Inicializa o gerenciador de email."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config = config
        self._load_data()
        self._start_queue_processor()

    def _load_data(self):
        """Carrega dados do sistema de arquivos."""
        self.templates: Dict[str, EmailTemplate] = {}
        self.messages: Dict[str, EmailMessage] = {}
        self.followups: Dict[str, FollowUpEmail] = {}
        self.queue: Dict[str, EmailQueue] = {}

        # Carregar templates
        templates_file = self.data_dir / "templates.json"
        if templates_file.exists():
            with open(templates_file, "r") as f:
                data = json.load(f)
                self.templates = {k: EmailTemplate(**v) for k, v in data.items()}

        # Carregar mensagens
        messages_file = self.data_dir / "messages.json"
        if messages_file.exists():
            with open(messages_file, "r") as f:
                data = json.load(f)
                self.messages = {k: EmailMessage(**v) for k, v in data.items()}

        # Carregar follow-ups
        followups_file = self.data_dir / "followups.json"
        if followups_file.exists():
            with open(followups_file, "r") as f:
                data = json.load(f)
                self.followups = {k: FollowUpEmail(**v) for k, v in data.items()}

        # Carregar fila
        queue_file = self.data_dir / "queue.json"
        if queue_file.exists():
            with open(queue_file, "r") as f:
                data = json.load(f)
                self.queue = {k: EmailQueue(**v) for k, v in data.items()}

    def _save_data(self):
        """Salva dados no sistema de arquivos."""
        # Salvar templates
        with open(self.data_dir / "templates.json", "w") as f:
            data = {k: v.dict() for k, v in self.templates.items()}
            json.dump(data, f, default=str, indent=2)

        # Salvar mensagens
        with open(self.data_dir / "messages.json", "w") as f:
            data = {k: v.dict() for k, v in self.messages.items()}
            json.dump(data, f, default=str, indent=2)

        # Salvar follow-ups
        with open(self.data_dir / "followups.json", "w") as f:
            data = {k: v.dict() for k, v in self.followups.items()}
            json.dump(data, f, default=str, indent=2)

        # Salvar fila
        with open(self.data_dir / "queue.json", "w") as f:
            data = {k: v.dict() for k, v in self.queue.items()}
            json.dump(data, f, default=str, indent=2)

    def _start_queue_processor(self):
        """Inicia o processador de fila em thread separada."""
        self.queue_processor = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self.queue_processor.start()

    def _process_queue(self):
        """Processa a fila de emails periodicamente."""
        while True:
            now = datetime.now()
            
            # Processar itens da fila
            for queue_item in sorted(
                self.queue.values(),
                key=lambda x: (x.priority, x.created_at)
            ):
                if (queue_item.status == "queued" and 
                    (not queue_item.next_try or queue_item.next_try <= now)):
                    try:
                        message = self.messages[queue_item.message_id]
                        self._send_email(message)
                        queue_item.status = "sent"
                    except Exception as e:
                        queue_item.retry_count += 1
                        queue_item.next_try = now + timedelta(
                            minutes=5 * queue_item.retry_count
                        )
                        queue_item.status = "failed"
                        message.error_message = str(e)
                        
                        if queue_item.retry_count >= 3:
                            queue_item.status = "failed"
            
            self._save_data()
            time.sleep(60)  # Verifica a cada minuto

    def create_template(self, template: EmailTemplate) -> EmailTemplate:
        """Cria um novo template de email."""
        self.templates[template.id] = template
        self._save_data()
        return template

    def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Retorna um template específico."""
        return self.templates.get(template_id)

    def create_message(self, template_id: str, context: dict) -> EmailMessage:
        """Cria uma mensagem a partir de um template."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} não encontrado")

        # Renderizar template
        subject = Template(template.subject_template).render(context)
        body = Template(template.body_template).render(context)

        # Criar mensagem
        message = EmailMessage(
            template_id=template_id,
            subject=subject,
            body=body,
            sender_email=self.config.sender_email,
            recipient_email=context["recipient_email"]
        )

        self.messages[message.id] = message
        self._save_data()
        return message

    def queue_message(self, message_id: str, priority: int = 3) -> EmailQueue:
        """Adiciona uma mensagem à fila de envio."""
        if message_id not in self.messages:
            raise ValueError(f"Mensagem {message_id} não encontrada")

        queue_item = EmailQueue(
            message_id=message_id,
            priority=priority
        )

        self.queue[queue_item.id] = queue_item
        self._save_data()
        return queue_item

    def _send_email(self, message: EmailMessage):
        """Envia um email usando SMTP."""
        if not self.config:
            raise ValueError("Configuração de email não definida")

        # Criar mensagem MIME
        mime_message = MIMEMultipart()
        mime_message["From"] = f"{self.config.sender_name} <{self.config.sender_email}>"
        mime_message["To"] = message.recipient_email
        mime_message["Subject"] = message.subject

        # Adicionar corpo
        body = message.body
        if self.config.signature:
            body += f"\n\n{self.config.signature}"
        mime_message.attach(MIMEText(body, "html"))

        # Adicionar anexos
        for attachment_path in message.attachments:
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=Path(attachment_path).name)
                part["Content-Disposition"] = f'attachment; filename="{Path(attachment_path).name}"'
                mime_message.attach(part)

        # Enviar email
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.smtp_user, self.config.smtp_password)
            server.send_message(mime_message)

        # Atualizar status
        message.status = "sent"
        message.sent_at = datetime.now()
        self._save_data()

    def schedule_followup(self, followup: FollowUpEmail) -> FollowUpEmail:
        """Agenda um email de follow-up."""
        self.followups[followup.id] = followup
        self._save_data()
        return followup

    def process_scheduled_followups(self):
        """Processa follow-ups agendados."""
        now = datetime.now()
        
        for followup in self.followups.values():
            if (followup.status == "pending" and 
                followup.scheduled_date <= now):
                try:
                    # Criar e enviar mensagem
                    message = self.create_message(
                        followup.template_id,
                        {"followup": followup}
                    )
                    self.queue_message(message.id, priority=2)
                    
                    # Atualizar status
                    followup.status = "sent"
                    followup.sent_at = now
                    followup.message_id = message.id
                except Exception as e:
                    followup.status = "failed"
                    print(f"Erro ao processar follow-up {followup.id}: {e}")

        self._save_data()

    def get_pending_followups(self) -> List[FollowUpEmail]:
        """Retorna follow-ups pendentes."""
        return [
            f for f in self.followups.values()
            if f.status == "pending"
        ]