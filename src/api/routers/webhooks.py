"""
Webhook endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.auth.router import get_current_user
from src.api.models.database_models import User
from src.api.models.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookRead,
    WebhookDeliveryRead,
    WebhookEvent
)
from src.api.services.webhook_service import WebhookService

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.post("", response_model=WebhookRead)
async def create_webhook(
    webhook: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new webhook."""
    try:
        webhook_service = WebhookService(db)
        return webhook_service.create_webhook(webhook, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[WebhookRead])
async def get_webhooks(
    event_type: Optional[str] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all webhooks."""
    webhook_service = WebhookService(db)
    return webhook_service.get_webhooks(event_type, active_only)

@router.get("/{webhook_id}", response_model=WebhookRead)
async def get_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific webhook."""
    webhook_service = WebhookService(db)
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook

@router.put("/{webhook_id}", response_model=WebhookRead)
async def update_webhook(
    webhook_id: int,
    webhook_update: WebhookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a webhook."""
    try:
        webhook_service = WebhookService(db)
        webhook = webhook_service.update_webhook(webhook_id, webhook_update)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return webhook
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a webhook."""
    try:
        webhook_service = WebhookService(db)
        if webhook_service.delete_webhook(webhook_id):
            return {"message": "Webhook deleted"}
        raise HTTPException(status_code=404, detail="Webhook not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trigger", response_model=List[WebhookDeliveryRead])
async def trigger_webhook_event(
    event: WebhookEvent,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a webhook event."""
    webhook_service = WebhookService(db)
    deliveries = await webhook_service.trigger_event(event)
    return deliveries

@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDeliveryRead])
async def get_webhook_deliveries(
    webhook_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get webhook delivery history."""
    webhook_service = WebhookService(db)
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook_service.get_deliveries(webhook_id, limit)

@router.post("/deliveries/{delivery_id}/retry", response_model=WebhookDeliveryRead)
async def retry_webhook_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retry a failed webhook delivery."""
    webhook_service = WebhookService(db)
    delivery = await webhook_service.retry_delivery(delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found or already successful"
        )
    return delivery