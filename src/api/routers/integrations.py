"""
Integration endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.auth.router import get_current_user
from src.api.models.database_models import User
from src.api.models.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationRead,
    IntegrationSyncLogRead,
    IntegrationProvider
)
from src.api.services.integration_service import IntegrationService
from src.api.integrations.providers import get_provider, get_providers_by_type

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

@router.get("/providers", response_model=List[IntegrationProvider])
async def get_providers(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get available integration providers."""
    if type:
        return get_providers_by_type(type)
    return list(get_providers_by_type(None))

@router.get("/providers/{provider_id}", response_model=IntegrationProvider)
async def get_provider_info(
    provider_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get provider information."""
    try:
        return get_provider(provider_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("", response_model=IntegrationRead)
async def create_integration(
    integration: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new integration."""
    try:
        integration_service = IntegrationService(db)
        return await integration_service.create_integration(
            integration,
            current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[IntegrationRead])
async def get_integrations(
    type: Optional[str] = None,
    provider: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all integrations."""
    integration_service = IntegrationService(db)
    return integration_service.get_integrations(type, provider)

@router.get("/{integration_id}", response_model=IntegrationRead)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific integration."""
    integration_service = IntegrationService(db)
    integration = integration_service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.put("/{integration_id}", response_model=IntegrationRead)
async def update_integration(
    integration_id: int,
    integration_update: IntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an integration."""
    try:
        integration_service = IntegrationService(db)
        integration = await integration_service.update_integration(
            integration_id,
            integration_update
        )
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return integration
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an integration."""
    try:
        integration_service = IntegrationService(db)
        if integration_service.delete_integration(integration_id):
            return {"message": "Integration deleted"}
        raise HTTPException(status_code=404, detail="Integration not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{integration_id}/sync", response_model=IntegrationSyncLogRead)
async def sync_integration(
    integration_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger integration sync."""
    try:
        integration_service = IntegrationService(db)
        return await integration_service.sync_integration(integration_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{integration_id}/sync-logs", response_model=List[IntegrationSyncLogRead])
async def get_sync_logs(
    integration_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get integration sync logs."""
    integration_service = IntegrationService(db)
    integration = integration_service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration_service.get_sync_logs(integration_id, limit)