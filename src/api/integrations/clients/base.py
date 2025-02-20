"""
Base integration client.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
from datetime import datetime

class IntegrationClient(ABC):
    """Base class for integration clients."""
    
    def __init__(self, config: Dict[str, Any], credentials: Dict[str, Any]):
        self.config = config
        self.credentials = credentials
        self._client = None
        self._last_error = None
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the client connection."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the integration is healthy."""
        pass

    @abstractmethod
    async def sync_data(self) -> Dict[str, int]:
        """Sync data with the integration."""
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._initialized

    @property
    def last_error(self) -> Optional[str]:
        """Get last error message."""
        return self._last_error

    def _set_error(self, error: str):
        """Set error message."""
        self._last_error = error

    def _clear_error(self):
        """Clear error message."""
        self._last_error = None

class CRMClient(IntegrationClient):
    """Base class for CRM integrations."""
    
    @abstractmethod
    async def get_contacts(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get contacts from CRM."""
        pass

    @abstractmethod
    async def create_contact(self, data: Dict) -> Dict:
        """Create contact in CRM."""
        pass

    @abstractmethod
    async def update_contact(self, contact_id: str, data: Dict) -> Dict:
        """Update contact in CRM."""
        pass

    @abstractmethod
    async def get_deals(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get deals from CRM."""
        pass

    @abstractmethod
    async def create_deal(self, data: Dict) -> Dict:
        """Create deal in CRM."""
        pass

    @abstractmethod
    async def update_deal(self, deal_id: str, data: Dict) -> Dict:
        """Update deal in CRM."""
        pass

class PaymentClient(IntegrationClient):
    """Base class for payment integrations."""
    
    @abstractmethod
    async def create_payment(self, amount: int, currency: str, metadata: Dict) -> Dict:
        """Create a payment."""
        pass

    @abstractmethod
    async def get_payment(self, payment_id: str) -> Dict:
        """Get payment details."""
        pass

    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict:
        """Refund a payment."""
        pass

    @abstractmethod
    async def create_subscription(self, customer_id: str, plan_id: str) -> Dict:
        """Create a subscription."""
        pass

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel a subscription."""
        pass

class EmailClient(IntegrationClient):
    """Base class for email integrations."""
    
    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        content: str,
        template_id: Optional[str] = None
    ) -> Dict:
        """Send an email."""
        pass

    @abstractmethod
    async def get_templates(self) -> List[Dict]:
        """Get email templates."""
        pass

    @abstractmethod
    async def get_stats(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get email statistics."""
        pass

    @abstractmethod
    async def get_template_stats(
        self,
        template_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get template statistics."""
        pass

class CalendarClient(IntegrationClient):
    """Base class for calendar integrations."""
    
    @abstractmethod
    async def get_events(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get calendar events."""
        pass

    @abstractmethod
    async def create_event(self, data: Dict) -> Dict:
        """Create calendar event."""
        pass

    @abstractmethod
    async def update_event(self, event_id: str, data: Dict) -> Dict:
        """Update calendar event."""
        pass

    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Delete calendar event."""
        pass

class StorageClient(IntegrationClient):
    """Base class for storage integrations."""
    
    @abstractmethod
    async def upload_file(self, file_path: str, destination: str) -> Dict:
        """Upload a file."""
        pass

    @abstractmethod
    async def download_file(self, file_path: str, destination: str) -> bool:
        """Download a file."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        pass

    @abstractmethod
    async def list_files(self, prefix: Optional[str] = None) -> List[Dict]:
        """List files."""
        pass