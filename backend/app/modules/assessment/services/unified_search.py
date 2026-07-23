from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.modules.assessment.models import Question
from app.modules.academic.models import Subject, Chapter, Topic, Exam
from app.modules.content.models import ContentItem


class UnifiedSearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_all(self, q: str, limit_per_entity: int = 5) -> Dict[str, Any]:
        q_term = f"%{q}%"

        # 1. Exams
        exams = self.db.execute(
            select(Exam).filter(
                or_(Exam.name.ilike(q_term), Exam.code.ilike(q_term)),
                Exam.is_deleted == False
            ).limit(limit_per_entity)
        ).scalars().all()

        # 2. Subjects
        subjects = self.db.execute(
            select(Subject).filter(
                Subject.name.ilike(q_term),
                Subject.is_deleted == False
            ).limit(limit_per_entity)
        ).scalars().all()

        # 3. Topics
        topics = self.db.execute(
            select(Topic).filter(
                Topic.name.ilike(q_term),
                Topic.is_deleted == False
            ).limit(limit_per_entity)
        ).scalars().all()

        # 4. ContentItems (Books, Videos, Notes)
        content_items = self.db.execute(
            select(ContentItem).filter(
                or_(ContentItem.title.ilike(q_term), ContentItem.description.ilike(q_term)),
                ContentItem.is_deleted == False
            ).limit(limit_per_entity)
        ).scalars().all()

        # 5. Questions
        questions = self.db.execute(
            select(Question).filter(
                or_(Question.content.ilike(q_term), Question.explanation.ilike(q_term)),
                Question.is_deleted == False
            ).limit(limit_per_entity)
        ).scalars().all()

        return {
            "query": q,
            "exams": [{"id": str(e.id), "name": e.name, "code": e.code} for e in exams],
            "subjects": [{"id": str(s.id), "name": s.name} for s in subjects],
            "topics": [{"id": str(t.id), "name": t.name, "chapter_id": str(t.chapter_id)} for t in topics],
            "content": [{"id": str(c.id), "title": c.title, "content_type": c.content_type.value, "slug": c.slug} for c in content_items],
            "questions": [{"id": str(q_item.id), "content": q_item.content[:100], "difficulty": q_item.difficulty.value} for q_item in questions],
        }
