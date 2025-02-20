"""
HubSpot CRM integration client.
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
import httpx
from src.api.integrations.clients.base import CRMClient

logger = logging.getLogger(__name__)

class HubSpotClient(CRMClient):
    """HubSpot CRM client implementation."""

    BASE_URL = "https://api.hubapi.com"
    
    async def initialize(self) -> bool:
        """Initialize HubSpot client."""
        try:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.credentials['access_token']}",
                    "Content-Type": "application/json"
                }
            )
            
            # Test connection
            await self.check_health()
            self._initialized = True
            return True
        except Exception as e:
            self._set_error(f"Failed to initialize HubSpot client: {str(e)}")
            return False

    async def check_health(self) -> bool:
        """Check HubSpot API health."""
        try:
            response = await self._client.get("/crm/v3/objects/contacts")
            return response.status_code == 200
        except Exception as e:
            self._set_error(f"HubSpot health check failed: {str(e)}")
            return False

    async def sync_data(self) -> Dict[str, int]:
        """Sync data with HubSpot."""
        stats = {
            "contacts_synced": 0,
            "contacts_failed": 0,
            "deals_synced": 0,
            "deals_failed": 0
        }

        if self.config.get("sync_contacts"):
            try:
                contacts = await self.get_contacts()
                stats["contacts_synced"] = len(contacts)
            except Exception as e:
                logger.error(f"Contact sync failed: {str(e)}")
                stats["contacts_failed"] += 1

        if self.config.get("sync_deals"):
            try:
                deals = await self.get_deals()
                stats["deals_synced"] = len(deals)
            except Exception as e:
                logger.error(f"Deal sync failed: {str(e)}")
                stats["deals_failed"] += 1

        return stats

    async def get_contacts(
        self,
        updated_since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get contacts from HubSpot."""
        params = {
            "limit": 100,
            "properties": ["email", "firstname", "lastname", "phone", "company"]
        }
        
        if updated_since:
            params["filter"] = {
                "lastmodifieddate": {
                    "after": int(updated_since.timestamp() * 1000)
                }
            }

        try:
            response = await self._client.get(
                "/crm/v3/objects/contacts",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            contacts = []
            for result in data["results"]:
                contacts.append({
                    "id": result["id"],
                    "email": result["properties"].get("email"),
                    "first_name": result["properties"].get("firstname"),
                    "last_name": result["properties"].get("lastname"),
                    "phone": result["properties"].get("phone"),
                    "company": result["properties"].get("company"),
                    "created_at": result["createdAt"],
                    "updated_at": result["updatedAt"]
                })
            
            return contacts
        except Exception as e:
            self._set_error(f"Failed to get contacts: {str(e)}")
            raise

    async def create_contact(self, data: Dict) -> Dict:
        """Create contact in HubSpot."""
        try:
            response = await self._client.post(
                "/crm/v3/objects/contacts",
                json={
                    "properties": {
                        "email": data["email"],
                        "firstname": data.get("first_name"),
                        "lastname": data.get("last_name"),
                        "phone": data.get("phone"),
                        "company": data.get("company")
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._set_error(f"Failed to create contact: {str(e)}")
            raise

    async def update_contact(self, contact_id: str, data: Dict) -> Dict:
        """Update contact in HubSpot."""
        try:
            response = await self._client.patch(
                f"/crm/v3/objects/contacts/{contact_id}",
                json={
                    "properties": {
                        "email": data.get("email"),
                        "firstname": data.get("first_name"),
                        "lastname": data.get("last_name"),
                        "phone": data.get("phone"),
                        "company": data.get("company")
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._set_error(f"Failed to update contact: {str(e)}")
            raise

    async def get_deals(
        self,
        updated_since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get deals from HubSpot."""
        params = {
            "limit": 100,
            "properties": ["dealname", "amount", "dealstage", "pipeline"]
        }
        
        if updated_since:
            params["filter"] = {
                "lastmodifieddate": {
                    "after": int(updated_since.timestamp() * 1000)
                }
            }

        try:
            response = await self._client.get(
                "/crm/v3/objects/deals",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            deals = []
            for result in data["results"]:
                deals.append({
                    "id": result["id"],
                    "name": result["properties"].get("dealname"),
                    "amount": result["properties"].get("amount"),
                    "stage": result["properties"].get("dealstage"),
                    "pipeline": result["properties"].get("pipeline"),
                    "created_at": result["createdAt"],
                    "updated_at": result["updatedAt"]
                })
            
            return deals
        except Exception as e:
            self._set_error(f"Failed to get deals: {str(e)}")
            raise

    async def create_deal(self, data: Dict) -> Dict:
        """Create deal in HubSpot."""
        try:
            response = await self._client.post(
                "/crm/v3/objects/deals",
                json={
                    "properties": {
                        "dealname": data["name"],
                        "amount": data.get("amount"),
                        "dealstage": data.get("stage"),
                        "pipeline": data.get("pipeline")
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._set_error(f"Failed to create deal: {str(e)}")
            raise

    async def update_deal(self, deal_id: str, data: Dict) -> Dict:
        """Update deal in HubSpot."""
        try:
            response = await self._client.patch(
                f"/crm/v3/objects/deals/{deal_id}",
                json={
                    "properties": {
                        "dealname": data.get("name"),
                        "amount": data.get("amount"),
                        "dealstage": data.get("stage"),
                        "pipeline": data.get("pipeline")
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._set_error(f"Failed to update deal: {str(e)}")
            raise

    async def __aenter__(self):
        """Async context manager enter."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()