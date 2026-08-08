from typing import Optional

from sqlalchemy.orm import Session

from models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    link: Optional[str] = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        link=link,
        read=False,
    )
    db.add(notification)
    return notification


def get_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.read.is_(False))
    if notification_type:
        query = query.filter(Notification.type == notification_type)

    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read.is_(False),
    ).count()
    data = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return data, total, unread_count
