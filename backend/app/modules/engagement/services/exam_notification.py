import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.modules.engagement.models import ExamNotification, Notification, UserNotification


class ExamNotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_official_notifications(self, limit: int = 20) -> List[ExamNotification]:
        return self.db.execute(
            select(ExamNotification)
            .filter(ExamNotification.is_active == True, ExamNotification.is_deleted == False)
            .order_by(ExamNotification.created_at.desc())
            .limit(limit)
        ).scalars().all()

    def get_exam_calendar(self) -> List[Dict[str, Any]]:
        notifications = self.list_official_notifications(limit=50)
        events = []
        for n in notifications:
            if n.exam_date:
                events.append({
                    "id": str(n.id),
                    "title": n.title,
                    "event_type": "EXAM_DATE",
                    "date": n.exam_date.isoformat() if hasattr(n.exam_date, 'isoformat') else str(n.exam_date),
                    "official_pdf_url": n.official_pdf_url,
                })
            if n.application_end_date:
                events.append({
                    "id": f"{n.id}_deadline",
                    "title": f"Deadline: {n.title}",
                    "event_type": "APPLICATION_DEADLINE",
                    "date": n.application_end_date.isoformat() if hasattr(n.application_end_date, 'isoformat') else str(n.application_end_date),
                    "official_pdf_url": n.official_pdf_url,
                })
        return events

    def get_user_notifications(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        user_notifs = self.db.execute(
            select(UserNotification)
            .filter(UserNotification.user_id == user_id, UserNotification.is_deleted == False)
            .order_by(UserNotification.created_at.desc())
        ).scalars().all()

        result = []
        for un in user_notifs:
            notif = un.notification
            if notif:
                result.append({
                    "id": str(un.id),
                    "notification_id": str(notif.id),
                    "title": notif.title,
                    "message": notif.message,
                    "is_read": un.is_read,
                    "created_at": un.created_at.isoformat() if hasattr(un.created_at, 'isoformat') else str(un.created_at),
                })
        return result

    def mark_read(self, user_id: uuid.UUID, user_notif_id: uuid.UUID) -> bool:
        un = self.db.execute(
            select(UserNotification).filter_by(id=user_notif_id, user_id=user_id)
        ).scalar_one_or_none()

        if un:
            un.is_read = True
            self.db.commit()
            return True
        return False
