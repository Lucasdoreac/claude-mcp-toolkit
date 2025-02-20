"""
CRUD operations for clients.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.api.crud.base import CRUDBase
from src.api.models.database_models import Client
from src.api.models.schemas import ClientCreate, ClientUpdate

class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    """Client specific CRUD operations."""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Client]:
        """Get client by email."""
        return db.query(Client).filter(Client.email == email).first()
    
    def get_by_status(self, db: Session, *, status: str) -> List[Client]:
        """Get all clients with a specific status."""
        return db.query(Client).filter(Client.status == status).all()
    
    def get_with_deals(self, db: Session, *, client_id: int) -> Optional[Client]:
        """Get client with their deals."""
        return db.query(Client).filter(Client.id == client_id).first()
    
    def update_status(
        self,
        db: Session,
        *,
        client_id: int,
        status: str
    ) -> Optional[Client]:
        """Update client status."""
        client = self.get(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        client.status = status
        db.commit()
        db.refresh(client)
        return client
    
    def search(self, db: Session, *, query: str) -> List[Client]:
        """Search clients by name or company."""
        return db.query(Client).filter(
            (Client.name.ilike(f"%{query}%")) |
            (Client.company.ilike(f"%{query}%"))
        ).all()

client = CRUDClient(Client)