"""
Dashboard router with caching.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.api.database import get_db
from src.api.auth.router import get_current_user
from src.api.models.database_models import User
from src.api.cache import cache_response, rate_limit
from src.api.crud.crud_deal import deal
from src.api.crud.crud_client import client
from src.api.crud.crud_proposal import proposal

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
@cache_response(expire=300)  # Cache for 5 minutes
@rate_limit("dashboard_stats")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    # Get basic metrics
    total_deals = len(deal.get_by_owner(db, owner_id=current_user.id))
    active_deals = len(deal.get_by_status(db, status="active"))
    total_proposals = len(proposal.get_by_owner(db, owner_id=current_user.id))
    total_clients = len(client.get_multi(db))

    # Get recent activity
    recent_deals = deal.get_multi(
        db,
        filters={"owner_id": current_user.id},
        limit=5
    )
    
    # Get pipeline stats
    pipeline_stats = {
        status: len(deal.get_by_status(db, status=status))
        for status in ["new", "contacted", "proposal_sent", "negotiation", "closed"]
    }
    
    # Get proposal stats
    proposal_stats = {
        "sent": len(proposal.get_by_status(db, status="sent")),
        "accepted": len(proposal.get_by_status(db, status="accepted")),
        "rejected": len(proposal.get_by_status(db, status="rejected")),
        "expired": len(proposal.get_expired(db))
    }

    return {
        "metrics": {
            "total_deals": total_deals,
            "active_deals": active_deals,
            "total_proposals": total_proposals,
            "total_clients": total_clients
        },
        "recent_activity": [
            {
                "id": d.id,
                "title": d.title,
                "status": d.status,
                "created_at": d.created_at
            }
            for d in recent_deals
        ],
        "pipeline_stats": pipeline_stats,
        "proposal_stats": proposal_stats
    }