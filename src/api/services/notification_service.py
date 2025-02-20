"""
Notification service for handling different types of notifications.
"""
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from src.api.models.notification import Notification, NotificationCreate
from src.api.services.email_service import send_email
from src.api.services.push_service import send_push_notification

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling notifications."""

    def __init__(self, db: Session, background_tasks: BackgroundTasks):
        self.db = db
        self.background_tasks = background_tasks

    async def create_notification(self, notification: NotificationCreate) -> Notification:
        """Create a new notification."""
        db_notification = Notification(
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            content=notification.content
        )
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)

        # Send notification based on type
        if notification.type == "email":
            self.background_tasks.add_task(
                self._send_email_notification,
                db_notification
            )
        elif notification.type == "push":
            self.background_tasks.add_task(
                self._send_push_notification,
                db_notification
            )

        return db_notification

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if notification:
            notification.read = True
            self.db.commit()
            self.db.refresh(notification)

        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        result = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).update({"read": True})
        
        self.db.commit()
        return result

    async def _send_email_notification(self, notification: Notification):
        """Send email notification."""
        try:
            await send_email(
                subject=notification.title,
                content=notification.content,
                recipient_id=notification.user_id
            )
            notification.delivered_at = datetime.utcnow()
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")

    async def _send_push_notification(self, notification: Notification):
        """Send push notification."""
        try:
            await send_push_notification(
                title=notification.title,
                message=notification.content,
                user_id=notification.user_id
            )
            notification.delivered_at = datetime.utcnow()
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")

    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Clean up notifications older than specified days."""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = self.db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.read == True
        ).delete()
        
        self.db.commit()
        return result