"""
Notification endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.auth.router import get_current_user
from src.api.models.database_models import User
from src.api.models.notification import NotificationCreate, NotificationRead
from src.api.services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationRead])
async def get_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, description="Maximum number of notifications to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Get user's notifications."""
    notification_service = NotificationService(db, background_tasks)
    return notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )

@router.post("", response_model=NotificationRead)
async def create_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a new notification."""
    if notification.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Can only create notifications for yourself unless superuser"
        )
    
    notification_service = NotificationService(db, background_tasks)
    return await notification_service.create_notification(notification)

@router.post("/{notification_id}/read", response_model=NotificationRead)
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Mark a notification as read."""
    notification_service = NotificationService(db, background_tasks)
    notification = notification_service.mark_as_read(notification_id, current_user.id)
    
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    
    return notification

@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Mark all notifications as read."""
    notification_service = NotificationService(db, background_tasks)
    count = notification_service.mark_all_as_read(current_user.id)
    return {"message": f"Marked {count} notifications as read"}

@router.delete("/cleanup")
async def cleanup_notifications(
    days: int = Query(30, description="Delete read notifications older than this many days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Clean up old notifications."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can cleanup notifications"
        )
    
    notification_service = NotificationService(db, background_tasks)
    count = notification_service.cleanup_old_notifications(days)
    return {"message": f"Deleted {count} old notifications"}