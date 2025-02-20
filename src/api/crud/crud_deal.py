"""
CRUD operations for deals.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.api.crud.base import CRUDBase
from src.api.models.database_models import Deal
from src.api.models.schemas import DealCreate, DealUpdate

class CRUDDeal(CRUDBase[Deal, DealCreate, DealUpdate]):
    """Deal specific CRUD operations."""
    
    def get_by_client(self, db: Session, *, client_id: int) -> List[Deal]:
        """Get all deals for a specific client."""
        return db.query(Deal).filter(Deal.client_id == client_id).all()
    
    def get_by_owner(self, db: Session, *, owner_id: int) -> List[Deal]:
        """Get all deals for a specific owner."""
        return db.query(Deal).filter(Deal.owner_id == owner_id).all()
    
    def get_by_status(self, db: Session, *, status: str) -> List[Deal]:
        """Get all deals with a specific status."""
        return db.query(Deal).filter(Deal.status == status).all()
    
    def get_by_priority(self, db: Session, *, priority: str) -> List[Deal]:
        """Get all deals with a specific priority."""
        return db.query(Deal).filter(Deal.priority == priority).all()
    
    def update_status(
        self,
        db: Session,
        *,
        deal_id: int,
        status: str
    ) -> Optional[Deal]:
        """Update deal status."""
        deal = self.get(db, deal_id)
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        deal.status = status
        db.commit()
        db.refresh(deal)
        return deal

deal = CRUDDeal(Deal)