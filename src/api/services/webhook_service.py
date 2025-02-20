"""
Webhook service for managing and delivering webhooks.
"""
import logging
import json
import hmac
import hashlib
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import httpx

from src.api.models.webhook import (
    Webhook,
    WebhookCreate,
    WebhookUpdate,
    WebhookDelivery,
    WebhookEvent
)

logger = logging.getLogger(__name__)

class WebhookService:
    """Service for managing webhooks."""

    def __init__(self, db: Session):
        self.db = db
        self._http_client = httpx.AsyncClient(timeout=30.0)

    def create_webhook(self, webhook: WebhookCreate, user_id: int) -> Webhook:
        """Create a new webhook."""
        db_webhook = Webhook(
            name=webhook.name,
            url=str(webhook.url),
            description=webhook.description,
            events=webhook.events,
            headers=webhook.headers,
            secret_key=webhook.secret_key,
            retry_count=webhook.retry_count,
            created_by=user_id
        )

        try:
            self.db.add(db_webhook)
            self.db.commit()
            self.db.refresh(db_webhook)
            return db_webhook
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error creating webhook")

    def get_webhook(self, webhook_id: int) -> Optional[Webhook]:
        """Get webhook by ID."""
        return self.db.query(Webhook).filter(Webhook.id == webhook_id).first()

    def get_webhooks(
        self,
        event_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Webhook]:
        """Get all webhooks."""
        query = self.db.query(Webhook)
        
        if active_only:
            query = query.filter(Webhook.is_active == True)
        
        if event_type:
            # Filter webhooks that subscribe to this event
            query = query.filter(Webhook.events.contains([event_type]))
            
        return query.all()

    def update_webhook(
        self,
        webhook_id: int,
        webhook_update: WebhookUpdate
    ) -> Optional[Webhook]:
        """Update a webhook."""
        webhook = self.get_webhook(webhook_id)
        if not webhook:
            return None

        update_dict = webhook_update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            # Convert URL to string if present
            if field == "url" and value:
                value = str(value)
            setattr(webhook, field, value)

        try:
            webhook.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(webhook)
            return webhook
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error updating webhook")

    def delete_webhook(self, webhook_id: int) -> bool:
        """Delete a webhook."""
        webhook = self.get_webhook(webhook_id)
        if not webhook:
            return False

        try:
            self.db.delete(webhook)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Cannot delete webhook with existing deliveries")

    async def trigger_event(self, event: WebhookEvent) -> List[WebhookDelivery]:
        """Trigger webhook event."""
        # Get active webhooks for this event
        webhooks = self.get_webhooks(event.event_type)
        if not webhooks:
            return []

        # Create delivery records
        deliveries = []
        for webhook in webhooks:
            delivery = WebhookDelivery(
                webhook_id=webhook.id,
                event_type=event.event_type,
                payload=event.payload
            )
            self.db.add(delivery)
            deliveries.append(delivery)
        self.db.commit()

        # Deliver webhooks asynchronously
        delivery_tasks = [
            self._deliver_webhook(webhook, delivery)
            for webhook, delivery in zip(webhooks, deliveries)
        ]
        await asyncio.gather(*delivery_tasks)

        return deliveries

    def get_deliveries(
        self,
        webhook_id: int,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """Get webhook delivery history."""
        return self.db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook_id
        ).order_by(
            WebhookDelivery.created_at.desc()
        ).limit(limit).all()

    async def retry_delivery(self, delivery_id: int) -> Optional[WebhookDelivery]:
        """Retry a failed webhook delivery."""
        delivery = self.db.query(WebhookDelivery).get(delivery_id)
        if not delivery or delivery.is_success:
            return None

        webhook = self.get_webhook(delivery.webhook_id)
        if not webhook or not webhook.is_active:
            return None

        # Reset delivery status
        delivery.attempt_count += 1
        delivery.response_status = None
        delivery.response_body = None
        delivery.error_message = None
        delivery.completed_at = None
        self.db.commit()

        # Attempt delivery
        await self._deliver_webhook(webhook, delivery)
        return delivery

    async def _deliver_webhook(
        self,
        webhook: Webhook,
        delivery: WebhookDelivery
    ) -> None:
        """Deliver webhook with retries."""
        max_attempts = webhook.retry_count
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            try:
                # Prepare request
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Claude-MCP-Webhook/1.0",
                    "X-Webhook-ID": str(webhook.id),
                    "X-Delivery-ID": str(delivery.id),
                    "X-Event-Type": delivery.event_type
                }

                if webhook.headers:
                    headers.update(webhook.headers)

                if webhook.secret_key:
                    signature = self._generate_signature(
                        webhook.secret_key,
                        delivery.payload
                    )
                    headers["X-Signature"] = signature

                # Send request
                response = await self._http_client.post(
                    webhook.url,
                    json=delivery.payload,
                    headers=headers
                )
                
                # Update delivery record
                delivery.response_status = response.status_code
                delivery.response_body = response.text
                delivery.is_success = 200 <= response.status_code < 300
                delivery.completed_at = datetime.utcnow()

                if delivery.is_success:
                    break

                # If failed but has retries left, wait before next attempt
                if attempt < max_attempts:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                delivery.error_message = str(e)
                delivery.is_success = False
                delivery.completed_at = datetime.utcnow()

                if attempt < max_attempts:
                    await asyncio.sleep(2 ** attempt)
            
            finally:
                self.db.commit()

    def _generate_signature(self, secret: str, payload: Dict[str, Any]) -> str:
        """Generate HMAC signature for webhook payload."""
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        return hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()

    async def close(self):
        """Close HTTP client."""
        await self._http_client.aclose()