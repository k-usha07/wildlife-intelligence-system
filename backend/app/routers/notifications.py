from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def get_notifications(
    priority: Optional[str] = None,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    from sqlalchemy import select
    query = select(Notification).where(Notification.user_id == current_user.id)
    if priority:
        query = query.where(Notification.priority == priority)
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
    result = await db.execute(query)
    notifications = result.scalars().all()

    return [
        {
            "id": str(n.id),
            "title": n.title,
            "message": n.message,
            "priority": n.priority,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.post("/")
async def create_notification(
    title: str,
    message: str,
    priority: str = "medium",
    notification_type: str = "info",
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    notif = Notification(
        user_id=current_user.id,
        title=title,
        message=message,
        priority=priority,
        type=notification_type,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return {
        "id": str(notif.id),
        "title": notif.title,
        "message": notif.message,
        "priority": notif.priority,
        "type": notif.type,
        "created_at": notif.created_at.isoformat(),
    }


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    return {"message": "Notification marked as read"}


@router.get("/unread-count")
async def unread_notification_count(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    from sqlalchemy import select, func
    count = await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    return {"unread_count": count}