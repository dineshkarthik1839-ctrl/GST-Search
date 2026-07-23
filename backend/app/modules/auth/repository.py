from sqlalchemy.orm import Session
from app.db.repository import BaseRepository
from app.modules.auth.models import UserSession, LoginHistory, VerificationToken

class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self, db: Session):
        super().__init__(UserSession, db)

class LoginHistoryRepository(BaseRepository[LoginHistory]):
    def __init__(self, db: Session):
        super().__init__(LoginHistory, db)

class VerificationTokenRepository(BaseRepository[VerificationToken]):
    def __init__(self, db: Session):
        super().__init__(VerificationToken, db)
