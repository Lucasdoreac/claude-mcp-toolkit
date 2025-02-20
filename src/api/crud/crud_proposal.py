"""
CRUD operations for proposals.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.api.crud.base import CRUDBase
from src.api.models.database_models import Proposal
from src.api.models.schemas import ProposalCreate, ProposalUpdate

class CRUDProposal(CRUDBase[Proposal, ProposalCreate, ProposalUpdate]):
    """Proposal specific CRUD operations."""
    
    def get_by_client(self, db: Session, *, client_id: int) -> List[Proposal]:
        """Get all proposals for a specific client."""
        return db.query(Proposal).filter(Proposal.client_id == client_id).all()
    
    def get_by_deal(self, db: Session, *, deal_id: int) -> List[Proposal]:
        """Get all proposals for a specific deal."""
        return db.query(Proposal).filter(Proposal.deal_id == deal_id).all()
    
    def get_by_owner(self, db: Session, *, owner_id: int) -> List[Proposal]:
        """Get all proposals for a specific owner."""
        return db.query(Proposal).filter(Proposal.owner_id == owner_id).all()
    
    def get_by_status(self, db: Session, *, status: str) -> List[Proposal]:
        """Get all proposals with a specific status."""
        return db.query(Proposal).filter(Proposal.status == status).all()
    
    def get_valid(self, db: Session) -> List[Proposal]:
        """Get all valid proposals (not expired)."""
        now = datetime.utcnow()
        return db.query(Proposal).filter(Proposal.valid_until > now).all()
    
    def get_expired(self, db: Session) -> List[Proposal]:
        """Get all expired proposals."""
        now = datetime.utcnow()
        return db.query(Proposal).filter(Proposal.valid_until <= now).all()
    
    def update_status(
        self,
        db: Session,
        *,
        proposal_id: int,
        status: str
    ) -> Optional[Proposal]:
        """Update proposal status."""
        proposal = self.get(db, proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposal not found"
            )
        proposal.status = status
        db.commit()
        db.refresh(proposal)
        return proposal

proposal = CRUDProposal(Proposal)