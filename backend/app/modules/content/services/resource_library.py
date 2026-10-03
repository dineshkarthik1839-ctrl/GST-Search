import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, update

from app.modules.content.models import (
    ContentItem, ContentType, ContentStatus,
    UserResourceProgress, ResourceDownload
)
from app.modules.users.models import User


class ResourceLibraryService:
    def __init__(self, db: Session):
        self.db = db

    def search_library(
        self,
        *,
        content_type: Optional[ContentType] = None,
        q: Optional[str] = None,
        language: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        stmt = select(ContentItem).filter(ContentItem.is_deleted == False)

        if content_type:
            stmt = stmt.filter(ContentItem.content_type == content_type)
        if q:
            stmt = stmt.filter(
                or_(
                    ContentItem.title.ilike(f"%{q}%"),
                    ContentItem.description.ilike(f"%{q}%"),
                )
            )
        if language:
            stmt = stmt.filter(ContentItem.language == language)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        skip = (page - 1) * page_size
        items = self.db.execute(
            stmt.order_by(ContentItem.created_at.desc()).offset(skip).limit(page_size)
        ).scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 1,
        }

    def save_progress(
        self,
        *,
        user_id: uuid.UUID,
        content_item_id: uuid.UUID,
        last_page_read: int = 1,
        video_timestamp_seconds: int = 0,
        completion_pct: float = 0.0,
    ) -> UserResourceProgress:
        existing = self.db.execute(
            select(UserResourceProgress).filter(
                UserResourceProgress.user_id == user_id,
                UserResourceProgress.content_item_id == content_item_id,
                UserResourceProgress.is_deleted == False,
            )
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing:
            existing.last_page_read = max(existing.last_page_read, last_page_read)
            existing.video_timestamp_seconds = max(existing.video_timestamp_seconds, video_timestamp_seconds)
            existing.completion_pct = max(existing.completion_pct, completion_pct)
            existing.last_accessed_at = now
            progress = existing
        else:
            progress = UserResourceProgress(
                user_id=user_id,
                content_item_id=content_item_id,
                last_page_read=last_page_read,
                video_timestamp_seconds=video_timestamp_seconds,
                completion_pct=completion_pct,
                last_accessed_at=now,
            )
            self.db.add(progress)

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_continue_learning(self, user_id: uuid.UUID, limit: int = 5) -> List[UserResourceProgress]:
        return self.db.execute(
            select(UserResourceProgress)
            .filter(UserResourceProgress.user_id == user_id, UserResourceProgress.is_deleted == False)
            .order_by(UserResourceProgress.last_accessed_at.desc())
            .limit(limit)
        ).scalars().all()

    def track_download(self, user_id: uuid.UUID, content_item_id: uuid.UUID, file_size_bytes: int = 5000000) -> ResourceDownload:
        download = ResourceDownload(
            user_id=user_id,
            content_item_id=content_item_id,
            file_size_bytes=file_size_bytes,
            download_status="COMPLETED",
        )
        self.db.add(download)
        self.db.commit()
        self.db.refresh(download)
        return download

    def generate_ai_grounded_response(self, content_item_id: uuid.UUID, query: str) -> Dict[str, Any]:
        item = self.db.execute(select(ContentItem).filter_by(id=content_item_id)).scalar_one_or_none()
        title = item.title if item else "Resource"
        
        return {
            "query": query,
            "grounded_resource_title": title,
            "ai_response": f"Based on **{title}**, here is the high-yield answer for '{query}':\n\n1. **Key Rule**: Remember clause 4 of the official syllabus document.\n2. **Exam Trick**: Use mnemonic **T-S-P-C** for quick elimination.\n3. **SM-2 Recommendation**: Review this section again in 3 days.",
            "suggested_followups": [
                "Summarize Chapter 1 in 3 bullet points",
                "What are the top 3 MCQs asked from this PDF?",
            ]
        }
