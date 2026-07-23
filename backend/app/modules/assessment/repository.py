import uuid
import hashlib
import math
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_, update

from app.db.repository import BaseRepository
from app.modules.assessment.models import (
    Question, QuestionOption, QuestionStatus, QuestionType,
    DifficultyLevel, BloomTaxonomy, QuestionRevision, QuestionAuditLog,
    QuestionReport, QuestionRelation
)

class QuestionRepository(BaseRepository[Question]):
    def __init__(self, db: Session):
        super().__init__(Question, db)

    def get_by_id(self, id: uuid.UUID) -> Optional[Question]:
        return self.db.execute(
            select(Question).filter(Question.id == id, Question.is_deleted == False)
        ).scalar_one_or_none()

    def generate_content_hash(self, content: str, topic_id: Optional[uuid.UUID] = None) -> str:
        clean_content = "".join(content.lower().split())
        topic_str = str(topic_id) if topic_id else ""
        return hashlib.sha256(f"{clean_content}:{topic_str}".encode('utf-8')).hexdigest()

    def check_duplicate(self, content: str, topic_id: Optional[uuid.UUID] = None) -> bool:
        # Check by content text and topic
        stmt = select(Question).filter(
            func.lower(Question.content) == content.lower(),
            Question.is_deleted == False
        )
        if topic_id:
            stmt = stmt.filter(Question.topic_id == topic_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def search(
        self,
        *,
        q: Optional[str] = None,
        subject_id: Optional[uuid.UUID] = None,
        chapter_id: Optional[uuid.UUID] = None,
        topic_id: Optional[uuid.UUID] = None,
        subtopic_id: Optional[uuid.UUID] = None,
        difficulty: Optional[DifficultyLevel] = None,
        bloom_taxonomy: Optional[BloomTaxonomy] = None,
        question_type: Optional[QuestionType] = None,
        language: Optional[str] = None,
        status: Optional[QuestionStatus] = None,
        verification_status: Optional[str] = None,
        source: Optional[str] = None,
        tag: Optional[str] = None,
        published_only: bool = False,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        if page is not None and page_size is not None:
            skip = (page - 1) * page_size
            limit = page_size

        stmt = select(Question).filter(Question.is_deleted == False)

        if q:
            stmt = stmt.filter(
                or_(
                    Question.content.ilike(f"%{q}%"),
                    Question.explanation.ilike(f"%{q}%"),
                    Question.source.ilike(f"%{q}%"),
                )
            )
        if subject_id:
            stmt = stmt.filter(Question.subject_id == subject_id)
        if chapter_id:
            stmt = stmt.filter(Question.chapter_id == chapter_id)
        if topic_id:
            stmt = stmt.filter(Question.topic_id == topic_id)
        if subtopic_id:
            stmt = stmt.filter(Question.subtopic_id == subtopic_id)
        if difficulty:
            stmt = stmt.filter(Question.difficulty == difficulty)
        if bloom_taxonomy:
            stmt = stmt.filter(Question.bloom_taxonomy == bloom_taxonomy)
        if question_type:
            stmt = stmt.filter(Question.question_type == question_type)
        if language:
            stmt = stmt.filter(Question.language == language)
        if status:
            stmt = stmt.filter(Question.status == status)
        if verification_status:
            stmt = stmt.filter(Question.verification_status == verification_status)
        if source:
            stmt = stmt.filter(Question.source.ilike(f"%{source}%"))
        if published_only:
            stmt = stmt.filter(Question.status == QuestionStatus.PUBLISHED)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        items = self.db.execute(
            stmt.order_by(Question.created_at.desc()).offset(skip).limit(limit)
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

    def bulk_update_status(self, ids: List[uuid.UUID], new_status: QuestionStatus) -> int:
        result = self.db.execute(
            update(Question)
            .where(Question.id.in_(ids), Question.is_deleted == False)
            .values(status=new_status, updated_at=datetime.now(timezone.utc))
        )
        self.db.commit()
        return result.rowcount


class QuestionRevisionRepository(BaseRepository[QuestionRevision]):
    def __init__(self, db: Session):
        super().__init__(QuestionRevision, db)

    def get_history(self, question_id: uuid.UUID) -> List[QuestionRevision]:
        return self.db.execute(
            select(QuestionRevision)
            .filter(
                QuestionRevision.question_id == question_id,
                QuestionRevision.is_deleted == False,
            )
            .order_by(QuestionRevision.version_number.desc())
        ).scalars().all()

    def get_latest_version_number(self, question_id: uuid.UUID) -> int:
        result = self.db.execute(
            select(func.max(QuestionRevision.version_number)).filter(
                QuestionRevision.question_id == question_id
            )
        ).scalar()
        return result or 0


class QuestionAuditLogRepository(BaseRepository[QuestionAuditLog]):
    def __init__(self, db: Session):
        super().__init__(QuestionAuditLog, db)

    def get_by_question(self, question_id: uuid.UUID) -> List[QuestionAuditLog]:
        return self.db.execute(
            select(QuestionAuditLog)
            .filter(QuestionAuditLog.question_id == question_id)
            .order_by(QuestionAuditLog.created_at.desc())
        ).scalars().all()


class QuestionReportRepository(BaseRepository[QuestionReport]):
    def __init__(self, db: Session):
        super().__init__(QuestionReport, db)

    def get_by_question(self, question_id: uuid.UUID) -> List[QuestionReport]:
        return self.db.execute(
            select(QuestionReport)
            .filter(QuestionReport.question_id == question_id, QuestionReport.is_deleted == False)
            .order_by(QuestionReport.created_at.desc())
        ).scalars().all()
