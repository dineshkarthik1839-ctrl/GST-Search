import uuid
import copy
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from app.modules.assessment.models import (
    Question, QuestionStatus, QuestionOption, QuestionRevision, QuestionAuditLog
)
from app.modules.assessment.repository import QuestionRepository, QuestionRevisionRepository
from app.core.logger import logger
from app.core.exceptions import AppException

ALLOWED_QUESTION_TRANSITIONS = {
    QuestionStatus.DRAFT: [QuestionStatus.SUBMITTED, QuestionStatus.ARCHIVED],
    QuestionStatus.SUBMITTED: [QuestionStatus.REVIEW, QuestionStatus.DRAFT],
    QuestionStatus.REVIEW: [
        QuestionStatus.APPROVED,
        QuestionStatus.CHANGES_REQUESTED,
        QuestionStatus.DRAFT,
    ],
    QuestionStatus.CHANGES_REQUESTED: [QuestionStatus.SUBMITTED],
    QuestionStatus.APPROVED: [QuestionStatus.PUBLISHED],
    QuestionStatus.PUBLISHED: [QuestionStatus.RETIRED, QuestionStatus.ARCHIVED],
    QuestionStatus.RETIRED: [QuestionStatus.ARCHIVED, QuestionStatus.DRAFT],
    QuestionStatus.ARCHIVED: [],
}

class QuestionWorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.question_repo = QuestionRepository(db)
        self.revision_repo = QuestionRevisionRepository(db)

    def _snapshot(self, question: Question) -> Dict[str, Any]:
        options_data = [
            {
                "id": str(opt.id),
                "content": opt.content,
                "option_index": opt.option_index,
                "is_correct": opt.is_correct,
                "explanation": opt.explanation,
            }
            for opt in (question.options or [])
        ]
        return {
            "id": str(question.id),
            "content": question.content,
            "question_type": question.question_type.value,
            "difficulty": question.difficulty.value,
            "bloom_taxonomy": question.bloom_taxonomy.value if question.bloom_taxonomy else None,
            "status": question.status.value,
            "verification_status": question.verification_status,
            "version": question.version,
            "marks": question.marks,
            "negative_marks": question.negative_marks,
            "language": question.language,
            "source": question.source,
            "explanation": question.explanation,
            "detailed_explanation": question.detailed_explanation,
            "quick_trick_explanation": question.quick_trick_explanation,
            "options": options_data,
            "tags": question.tags,
            "ai_metadata": question.ai_metadata,
            "snapshotted_at": datetime.now(timezone.utc).isoformat(),
        }

    def _audit(
        self,
        question: Question,
        action: str,
        old_status: Optional[QuestionStatus],
        new_status: Optional[QuestionStatus],
        performed_by_id: Optional[uuid.UUID],
        notes: Optional[str] = None,
    ):
        log = QuestionAuditLog(
            question_id=question.id,
            action=action,
            old_status=old_status.value if old_status else None,
            new_status=new_status.value if new_status else None,
            performed_by_id=performed_by_id,
            notes=notes,
        )
        self.db.add(log)

    def create_revision(
        self,
        question: Question,
        performed_by_id: Optional[uuid.UUID],
        change_summary: Optional[str] = None,
    ):
        next_version = self.revision_repo.get_latest_version_number(question.id) + 1
        revision = QuestionRevision(
            question_id=question.id,
            version_number=next_version,
            snapshot=self._snapshot(question),
            created_by_id=performed_by_id,
            change_summary=change_summary or f"Status changed to {question.status.value}",
        )
        self.db.add(revision)

    def transition(
        self,
        question_id: uuid.UUID,
        new_status: QuestionStatus,
        performed_by_id: Optional[uuid.UUID] = None,
        notes: Optional[str] = None,
    ) -> Question:
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise AppException(message="Question not found", status_code=404)

        old_status = question.status
        allowed = ALLOWED_QUESTION_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise AppException(
                message=f"Invalid question transition: {old_status.value} → {new_status.value}. "
                        f"Allowed: {[s.value for s in allowed]}",
                status_code=422,
            )

        # Save revision snapshot BEFORE mutating
        self.create_revision(question, performed_by_id, notes)

        # Apply transition
        question.status = new_status
        question.updated_at = datetime.now(timezone.utc)

        self._audit(question, "STATUS_CHANGED", old_status, new_status, performed_by_id, notes)
        self.db.commit()
        self.db.refresh(question)
        logger.info(f"Question {question.id} transitioned {old_status.value} → {new_status.value}")
        return question

    def spawn_draft_from_published(
        self,
        question_id: uuid.UUID,
        performed_by_id: Optional[uuid.UUID] = None,
    ) -> Question:
        """
        Clone a PUBLISHED/RETIRED Question as a new DRAFT.
        The original remains PUBLISHED and immutable.
        """
        original = self.question_repo.get_by_id(question_id)
        if not original:
            raise AppException(message="Question not found", status_code=404)
        if original.status not in (QuestionStatus.PUBLISHED, QuestionStatus.RETIRED):
            raise AppException(
                message="Only PUBLISHED or RETIRED questions can spawn a new Draft. Use transition() for other statuses.",
                status_code=422,
            )

        draft = Question(
            content=original.content,
            question_type=original.question_type,
            difficulty=original.difficulty,
            bloom_taxonomy=original.bloom_taxonomy,
            status=QuestionStatus.DRAFT,
            verification_status="UNVERIFIED",
            creation_source=original.creation_source,
            author_id=performed_by_id or original.author_id,
            subject_id=original.subject_id,
            chapter_id=original.chapter_id,
            topic_id=original.topic_id,
            subtopic_id=original.subtopic_id,
            learning_objective_id=original.learning_objective_id,
            marks=original.marks,
            negative_marks=original.negative_marks,
            language=original.language,
            source=original.source,
            reference_book=original.reference_book,
            estimated_time_seconds=original.estimated_time_seconds,
            explanation=original.explanation,
            detailed_explanation=original.detailed_explanation,
            quick_trick_explanation=original.quick_trick_explanation,
            video_explanation_url=original.video_explanation_url,
            tags=copy.deepcopy(original.tags) if original.tags else None,
            ai_metadata=copy.deepcopy(original.ai_metadata) if original.ai_metadata else None,
            analytics_summary={"attempt_count": 0, "correct_count": 0},
        )
        self.db.add(draft)
        self.db.flush()

        for opt in original.options:
            draft_opt = QuestionOption(
                question_id=draft.id,
                content=opt.content,
                option_index=opt.option_index,
                is_correct=opt.is_correct,
                explanation=opt.explanation,
            )
            self.db.add(draft_opt)

        self.db.commit()
        self.db.refresh(draft)

        self._audit(
            draft, "DRAFT_SPAWNED_FROM_PUBLISHED",
            None, QuestionStatus.DRAFT, performed_by_id,
            f"Spawned from published question {original.id}",
        )
        self.create_revision(draft, performed_by_id, f"Initial draft cloned from {original.id}")
        self.db.commit()

        logger.info(f"Spawned new question draft {draft.id} from published {original.id}")
        return draft
