import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.db.repository import BaseRepository
from app.modules.engagement.models import Bookmark, BookmarkType


class BookmarkRepository(BaseRepository[Bookmark]):
    def __init__(self, db: Session):
        super().__init__(Bookmark, db)

    def is_bookmarked(self, user_id: uuid.UUID, entity_type: BookmarkType, entity_id: uuid.UUID) -> bool:
        return self.db.execute(
            select(Bookmark).filter(
                Bookmark.user_id == user_id,
                Bookmark.entity_type == entity_type,
                Bookmark.entity_id == entity_id,
                Bookmark.is_deleted == False
            )
        ).scalar_one_or_none() is not None

    def toggle_bookmark(self, user_id: uuid.UUID, entity_type: BookmarkType, entity_id: uuid.UUID) -> bool:
        existing = self.db.execute(
            select(Bookmark).filter(
                Bookmark.user_id == user_id,
                Bookmark.entity_type == entity_type,
                Bookmark.entity_id == entity_id,
                Bookmark.is_deleted == False
            )
        ).scalar_one_or_none()

        if existing:
            self.db.delete(existing)
            self.db.commit()
            return False  # Removed bookmark
        else:
            bookmark = Bookmark(user_id=user_id, entity_type=entity_type, entity_id=entity_id)
            self.db.add(bookmark)
            self.db.commit()
            return True  # Added bookmark

    def get_user_bookmarks(self, user_id: uuid.UUID, entity_type: Optional[BookmarkType] = None) -> List[Bookmark]:
        stmt = select(Bookmark).filter(Bookmark.user_id == user_id, Bookmark.is_deleted == False)
        if entity_type:
            stmt = stmt.filter(Bookmark.entity_type == entity_type)
        return self.db.execute(stmt.order_by(Bookmark.created_at.desc())).scalars().all()
