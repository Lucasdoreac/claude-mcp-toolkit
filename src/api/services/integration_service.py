"""
Integration service for managing external integrations.
"""
import logging
from typing import Optional, List, Dict, Type
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.api.models.integration import (
    Integration,
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationSyncLog,
    IntegrationSyncLogCreate
)
from src.api.integrations.providers import (
    get_provider,
    validate_config,
    validate_credentials
)
from src.api.integrations.clients.base import IntegrationClient
from src.api.integrations.clients.hubspot import HubSpotClient

logger = logging.getLogger(__name__)

# Map of provider types to client classes
CLIENT_CLASSES = {
    "hubspot": HubSpotClient,
    # Add other providers here as they are implemented
}

class IntegrationService:
    """Service for managing integrations."""

    def __init__(self, db: Session):
        self.db = db

    async def create_integration(
        self,
        integration: IntegrationCreate,
        user_id: int
    ) -> Integration:
        """Create a new integration."""
        # Validate provider
        provider = get_provider(integration.provider)
        
        # Validate config and credentials
        if not validate_config(provider, integration.config):
            raise ValueError("Invalid configuration")
        if not validate_credentials(provider, integration.credentials):
            raise ValueError("Invalid credentials")

        # Create integration
        db_integration = Integration(
            name=integration.name,
            type=provider.type,
            provider=integration.provider,
            config=integration.config,
            credentials=integration.credentials,
            created_by=user_id
        )

        try:
            # Test connection
            client = self._get_client(db_integration)
            if not await client.initialize():
                raise ValueError(f"Connection test failed: {client.last_error}")

            # Save to database
            self.db.add(db_integration)
            self.db.commit()
            self.db.refresh(db_integration)
            return db_integration
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create integration: {str(e)}")

    def get_integration(self, integration_id: int) -> Optional[Integration]:
        """Get integration by ID."""
        return self.db.query(Integration).filter(
            Integration.id == integration_id
        ).first()

    def get_integrations(
        self,
        type: Optional[str] = None,
        provider: Optional[str] = None
    ) -> List[Integration]:
        """Get all integrations with optional filtering."""
        query = self.db.query(Integration)
        
        if type:
            query = query.filter(Integration.type == type)
        if provider:
            query = query.filter(Integration.provider == provider)
            
        return query.all()

    async def update_integration(
        self,
        integration_id: int,
        update_data: IntegrationUpdate
    ) -> Optional[Integration]:
        """Update an integration."""
        integration = self.get_integration(integration_id)
        if not integration:
            return None

        # Get provider
        provider = get_provider(integration.provider)

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        
        # Validate new config if provided
        if "config" in update_dict:
            if not validate_config(provider, update_dict["config"]):
                raise ValueError("Invalid configuration")
            integration.config = update_dict["config"]

        # Validate new credentials if provided
        if "credentials" in update_dict:
            if not validate_credentials(provider, update_dict["credentials"]):
                raise ValueError("Invalid credentials")
            integration.credentials = update_dict["credentials"]

        if "name" in update_dict:
            integration.name = update_dict["name"]
        if "is_enabled" in update_dict:
            integration.is_enabled = update_dict["is_enabled"]

        try:
            # Test connection if config or credentials changed
            if "config" in update_dict or "credentials" in update_dict:
                client = self._get_client(integration)
                if not await client.initialize():
                    raise ValueError(f"Connection test failed: {client.last_error}")

            # Save changes
            integration.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(integration)
            return integration
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update integration: {str(e)}")

    def delete_integration(self, integration_id: int) -> bool:
        """Delete an integration."""
        integration = self.get_integration(integration_id)
        if not integration:
            return False

        try:
            self.db.delete(integration)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Cannot delete integration with existing sync logs")

    async def sync_integration(self, integration_id: int) -> IntegrationSyncLog:
        """Sync data with integration."""
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError("Integration not found")

        if not integration.is_enabled:
            raise ValueError("Integration is disabled")

        # Create sync log
        sync_log = IntegrationSyncLog(
            integration_id=integration_id,
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(sync_log)
        self.db.commit()

        try:
            # Initialize client
            client = self._get_client(integration)
            if not await client.initialize():
                raise ValueError(f"Failed to initialize client: {client.last_error}")

            # Run sync
            stats = await client.sync_data()

            # Update sync log with success
            sync_log.status = "success"
            sync_log.items_processed = sum(stats.values())
            sync_log.items_succeeded = stats.get("synced", 0)
            sync_log.items_failed = stats.get("failed", 0)
            sync_log.completed_at = datetime.utcnow()

            # Update integration last sync
            integration.last_sync = sync_log.completed_at
            integration.status = "active"
            integration.error_message = None

        except Exception as e:
            # Update sync log with error
            sync_log.status = "error"
            sync_log.error_message = str(e)
            sync_log.completed_at = datetime.utcnow()

            # Update integration status
            integration.status = "error"
            integration.error_message = str(e)

        finally:
            self.db.commit()
            self.db.refresh(sync_log)
            return sync_log

    def get_sync_logs(
        self,
        integration_id: int,
        limit: int = 100
    ) -> List[IntegrationSyncLog]:
        """Get sync logs for an integration."""
        return self.db.query(IntegrationSyncLog).filter(
            IntegrationSyncLog.integration_id == integration_id
        ).order_by(
            IntegrationSyncLog.started_at.desc()
        ).limit(limit).all()

    def _get_client(self, integration: Integration) -> IntegrationClient:
        """Get integration client instance."""
        client_class = CLIENT_CLASSES.get(integration.provider)
        if not client_class:
            raise ValueError(f"No client implementation for provider: {integration.provider}")

        return client_class(
            config=integration.config,
            credentials=integration.credentials
        )