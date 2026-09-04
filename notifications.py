from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.models.notification import Notification
from app.schemas.notification import NotificationSchema

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationSchema])
def get_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Fetch notifications for current logged in user
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    return notifs
