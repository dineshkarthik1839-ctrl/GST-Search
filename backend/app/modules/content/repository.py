"""
Content Repository - Advanced querying, filtering, pagination, bulk ops.
"""
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_
from sqlalchemy.exc import IntegrityError

from app.db.repository import BaseRepository
from app.modules.content.models import (
    ContentItem, ContentType, ContentStatus,
    ContentRevision, ContentAuditLog,
    VideoDetails, BookDetails, PdfDetails,
    QuizDetails, FlashCardDetails, MindMapDetails,
    Resource,
)


class ContentRepository(BaseRepository[ContentItem]):
    def __init__(self, db: Session):
        super().__init__(ContentItem, db)

    def get_by_slug(self, slug: str) -> Optional[ContentItem]:
        return self.db.execute(
            select(ContentItem).filter(
                ContentItem.slug == slug,
                ContentItem.is_deleted == False
            )
        ).scalars().first()

    def search(
        self,
        *,
        q: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        status: Optional[ContentStatus] = None,
        language: Optional[str] = None,
        author_id: Optional[uuid.UUID] = None,
        published_only: bool = False,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        import math
        if page is not None and page_size is not None:
            skip = (page - 1) * page_size
            limit = page_size

        stmt = select(ContentItem).filter(ContentItem.is_deleted == False)

        if q:
            stmt = stmt.filter(
                or_(
                    ContentItem.title.ilike(f"%{q}%"),
                    ContentItem.description.ilike(f"%{q}%"),
                )
            )
        if content_type:
            stmt = stmt.filter(ContentItem.content_type == content_type)
        if status:
            stmt = stmt.filter(ContentItem.status == status)
        if language:
            stmt = stmt.filter(ContentItem.language == language)
        if author_id:
            stmt = stmt.filter(ContentItem.author_id == author_id)
        if published_only:
            now = datetime.now(timezone.utc)
            stmt = stmt.filter(
                ContentItem.status == ContentStatus.PUBLISHED,
                or_(ContentItem.publish_date == None, ContentItem.publish_date <= now),
                or_(ContentItem.expiry_date == None, ContentItem.expiry_date >= now),
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        items = self.db.execute(
            stmt.order_by(ContentItem.created_at.desc()).offset(skip).limit(limit)
        ).scalars().all()

        calc_page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total / limit) if (limit > 0 and total > 0) else 1

        return {
            "items": items,
            "total": total,
            "page": calc_page,
            "size": limit,
            "page_size": limit,
            "total_pages": total_pages,
        }

    def get_due_for_publish(self) -> List[ContentItem]:
        """Returns SCHEDULED items whose publish_date has passed."""
        now = datetime.now(timezone.utc)
        return self.db.execute(
            select(ContentItem).filter(
                ContentItem.status == ContentStatus.SCHEDULED,
                ContentItem.publish_date <= now,
                ContentItem.is_deleted == False,
            )
        ).scalars().all()

    def bulk_update_status(
        self, ids: List[uuid.UUID], new_status: ContentStatus
    ) -> int:
        from sqlalchemy import update
        result = self.db.execute(
            update(ContentItem)
            .where(ContentItem.id.in_(ids), ContentItem.is_deleted == False)
            .values(status=new_status, updated_at=datetime.now(timezone.utc))
        )
        self.db.commit()
        return result.rowcount

    def check_duplicate(self, title: str, content_type: ContentType) -> bool:
        return self.db.execute(
            select(ContentItem).filter(
                ContentItem.title == title,
                ContentItem.content_type == content_type,
                ContentItem.is_deleted == False,
            )
        ).scalar_one_or_none() is not None


class ContentRevisionRepository(BaseRepository[ContentRevision]):
    def __init__(self, db: Session):
        super().__init__(ContentRevision, db)

    def get_history(self, content_item_id: uuid.UUID) -> List[ContentRevision]:
        return self.db.execute(
            select(ContentRevision)
            .filter(
                ContentRevision.content_item_id == content_item_id,
                ContentRevision.is_deleted == False,
            )
            .order_by(ContentRevision.version_number.desc())
        ).scalars().all()

    def get_latest_version_number(self, content_item_id: uuid.UUID) -> int:
        result = self.db.execute(
            select(func.max(ContentRevision.version_number)).filter(
                ContentRevision.content_item_id == content_item_id
            )
        ).scalar()
        return result or 0


class ContentAuditLogRepository(BaseRepository[ContentAuditLog]):
    def __init__(self, db: Session):
        super().__init__(ContentAuditLog, db)

    def get_by_content_item(self, content_item_id: uuid.UUID) -> List[ContentAuditLog]:
        return self.db.execute(
            select(ContentAuditLog)
            .filter(ContentAuditLog.content_item_id == content_item_id)
            .order_by(ContentAuditLog.created_at.desc())
        ).scalars().all()


class ResourceRepository(BaseRepository[Resource]):
    def __init__(self, db: Session):
        super().__init__(Resource, db)

    def get_by_topic(self, topic_id: uuid.UUID) -> List[Resource]:
        return self.db.execute(
            select(Resource).filter(
                Resource.topic_id == topic_id,
                Resource.is_deleted == False,
            )
        ).scalars().all()
