from sqlalchemy.orm import Session
from app.db.repository import BaseRepository
from app.modules.engagement.models import Bookmark, UserProgress, StudyPlan, StudySession, Notification, UserNotification, Discussion, Comment, PhysicalActivity

class BookmarkRepository(BaseRepository[Bookmark]):
    def __init__(self, db: Session):
        super().__init__(Bookmark, db)

class UserProgressRepository(BaseRepository[UserProgress]):
    def __init__(self, db: Session):
        super().__init__(UserProgress, db)

class StudyPlanRepository(BaseRepository[StudyPlan]):
    def __init__(self, db: Session):
        super().__init__(StudyPlan, db)

class StudySessionRepository(BaseRepository[StudySession]):
    def __init__(self, db: Session):
        super().__init__(StudySession, db)

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

class UserNotificationRepository(BaseRepository[UserNotification]):
    def __init__(self, db: Session):
        super().__init__(UserNotification, db)

class DiscussionRepository(BaseRepository[Discussion]):
    def __init__(self, db: Session):
        super().__init__(Discussion, db)

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)

class PhysicalActivityRepository(BaseRepository[PhysicalActivity]):
    def __init__(self, db: Session):
        super().__init__(PhysicalActivity, db)
