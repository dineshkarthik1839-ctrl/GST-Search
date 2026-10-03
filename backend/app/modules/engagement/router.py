import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_optional
from app.modules.users.models import User
from app.modules.engagement.services.exam_notification import ExamNotificationService
from app.modules.assessment.router import _get_active_user_id

router = APIRouter(prefix="/engagement", tags=["Engagement & Exam Notifications"])


@router.get("/exam-notifications", summary="List official recruitment notifications")
def list_exam_notifications(db: Session = Depends(get_db)):
    svc = ExamNotificationService(db)
    items = svc.list_official_notifications()
    return [
        {
            "id": str(n.id),
            "title": n.title,
            "notification_type": n.notification_type,
            "official_pdf_url": n.official_pdf_url,
            "application_start_date": n.application_start_date.isoformat() if n.application_start_date else None,
            "application_end_date": n.application_end_date.isoformat() if n.application_end_date else None,
            "exam_date": n.exam_date.isoformat() if n.exam_date else None,
            "is_active": n.is_active,
        }
        for n in items
    ]


@router.get("/exam-calendar", summary="Get official exam calendar events")
def get_exam_calendar(db: Session = Depends(get_db)):
    svc = ExamNotificationService(db)
    return svc.get_exam_calendar()


@router.get("/notifications", summary="Get user notification center feed")
def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    svc = ExamNotificationService(db)
    user_id = _get_active_user_id(db, current_user)
    return svc.get_user_notifications(user_id=user_id)


@router.post("/notifications/{user_notification_id}/read", summary="Mark user notification read")
def mark_notification_read(
    user_notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    svc = ExamNotificationService(db)
    user_id = _get_active_user_id(db, current_user)
    success = svc.mark_read(user_id=user_id, user_notif_id=user_notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "READ"}
