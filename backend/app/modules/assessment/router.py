import uuid
import csv
import io
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user_optional, RequireRole
from app.modules.users.models import User
from app.modules.assessment.models import (
    Question, QuestionOption, QuestionStatus, QuestionType,
    DifficultyLevel, BloomTaxonomy, QuestionReport, Attempt, ExamResult
)
from app.modules.assessment.repository import (
    QuestionRepository, QuestionRevisionRepository,
    QuestionAuditLogRepository, QuestionReportRepository
)
from app.modules.assessment.service import QuestionWorkflowService
from app.modules.assessment.schemas import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionListResponse, QuestionRevisionResponse,
    QuestionAuditLogResponse, QuestionReportCreate, QuestionReportResponse,
    QuestionTransitionRequest, QuestionBulkStatusRequest,
    QuestionBulkImportRequest, QuestionBulkImportResponse,
    AttemptResponse, StartPracticeRequest, SaveAnswerRequest,
    ExamResultResponse, BookmarkToggleRequest, BookmarkResponse
)
from app.core.logger import logger
from app.core.exceptions import AppException

router = APIRouter(prefix="/questions", tags=["Questions & Question Intelligence Platform"])


def _get_active_user_id(db: Session, current_user: Optional[User]) -> uuid.UUID:
    if current_user:
        return current_user.id
    user = db.query(User).filter_by(is_active=True).first()
    if user:
        return user.id
    guest = User(email=f"guest_{uuid.uuid4().hex[:6]}@example.com", password_hash="hash", full_name="Guest Student")
    db.add(guest)
    db.commit()
    return guest.id


# ─────────────────────── Static Platform & Bulk Endpoints (Before /{id}) ─────

@router.get("/bookmarks", summary="Get user bookmarks")
def list_bookmarks(
    entity_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.engagement.repository import BookmarkRepository
    from app.modules.engagement.models import BookmarkType
    repo = BookmarkRepository(db)
    user_id = _get_active_user_id(db, current_user)
    type_enum = BookmarkType(entity_type) if (entity_type and entity_type.strip()) else None
    bookmarks = repo.get_user_bookmarks(user_id=user_id, entity_type=type_enum)
    return [{"id": str(b.id), "entity_type": b.entity_type.value, "entity_id": str(b.entity_id), "created_at": b.created_at} for b in bookmarks]


@router.post("/bookmarks/toggle", summary="Toggle bookmark on Question or Resource")
def toggle_bookmark(
    payload: BookmarkToggleRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.engagement.repository import BookmarkRepository
    from app.modules.engagement.models import BookmarkType
    repo = BookmarkRepository(db)
    user_id = _get_active_user_id(db, current_user)
    type_enum = BookmarkType(payload.entity_type)
    is_bookmarked = repo.toggle_bookmark(user_id=user_id, entity_type=type_enum, entity_id=payload.entity_id)
    return {"bookmarked": is_bookmarked}


@router.get("/search/unified", summary="Unified search across Questions, Topics, Content & Exams")
def unified_search(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    from app.modules.assessment.services.unified_search import UnifiedSearchService
    svc = UnifiedSearchService(db)
    return svc.search_all(q=q)


@router.get("/analytics/dashboard", summary="Get student performance analytics dashboard")
def get_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.assessment.services.analytics_engine import AnalyticsEngineService
    svc = AnalyticsEngineService(db)
    user_id = _get_active_user_id(db, current_user)
    return svc.get_student_dashboard(user_id=user_id)


@router.get("/analytics/leaderboard", summary="Get exam leaderboard")
def get_leaderboard(
    period: str = Query(default="ALL_TIME"),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.modules.assessment.services.analytics_engine import AnalyticsEngineService
    svc = AnalyticsEngineService(db)
    return svc.get_leaderboard(period=period, limit=limit)


@router.post("/practice/start", response_model=AttemptResponse, summary="Start practice session")
def start_practice_session(
    payload: StartPracticeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.assessment.services.assessment_engine import AssessmentEngineService
    svc = AssessmentEngineService(db)
    user_id = _get_active_user_id(db, current_user)
    return svc.start_practice_session(
        user_id=user_id,
        mode=payload.mode,
        subject_id=payload.subject_id,
        topic_id=payload.topic_id,
        num_questions=payload.num_questions
    )


@router.post("/tests/{mock_test_id}/start", response_model=AttemptResponse, summary="Start mock test session")
def start_mock_test(
    mock_test_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.assessment.services.assessment_engine import AssessmentEngineService
    svc = AssessmentEngineService(db)
    user_id = _get_active_user_id(db, current_user)
    return svc.start_mock_test(user_id=user_id, mock_test_id=mock_test_id)


@router.get("/attempts/{attempt_id}", response_model=AttemptResponse, summary="Get attempt state")
def get_attempt_state(attempt_id: uuid.UUID, db: Session = Depends(get_db)):
    attempt = db.execute(select(Attempt).filter(Attempt.id == attempt_id, Attempt.is_deleted == False)).scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt


@router.post("/attempts/{attempt_id}/questions/{question_id}/answer", summary="Save question answer / mark for review")
def save_answer(
    attempt_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: SaveAnswerRequest,
    db: Session = Depends(get_db),
):
    from app.modules.assessment.services.assessment_engine import AssessmentEngineService
    svc = AssessmentEngineService(db)
    aq = svc.save_question_response(
        attempt_id=attempt_id,
        question_id=question_id,
        selected_option_id=payload.selected_option_id,
        user_answer_text=payload.user_answer_text,
        status=payload.status,
        time_spent_seconds=payload.time_spent_seconds
    )
    return {"status": "SAVED", "attempt_question_id": str(aq.id)}


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResponse, summary="Submit & grade attempt")
def submit_attempt(
    attempt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.assessment.services.assessment_engine import AssessmentEngineService
    svc = AssessmentEngineService(db)
    user_id = _get_active_user_id(db, current_user)
    return svc.submit_attempt(attempt_id=attempt_id, user_id=user_id)


@router.get("/attempts/{attempt_id}/result", response_model=ExamResultResponse, summary="Get exam result report")
def get_exam_result(attempt_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.execute(select(ExamResult).filter(ExamResult.attempt_id == attempt_id)).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/export/csv", summary="Export question bank as CSV")
def export_questions_csv(
    subject_id: Optional[uuid.UUID] = Query(default=None),
    difficulty: Optional[DifficultyLevel] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = QuestionRepository(db)
    result = repo.search(subject_id=subject_id, difficulty=difficulty, limit=10000)
    items = result["items"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "content", "question_type", "difficulty", "bloom_taxonomy", "status", "language", "created_at"])
    for q in items:
        writer.writerow([
            str(q.id), q.content, q.question_type.value, q.difficulty.value,
            q.bloom_taxonomy.value if q.bloom_taxonomy else "",
            q.status.value, q.language, q.created_at.isoformat()
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=questions_export.csv"},
    )


@router.post("/bulk/status", response_model=dict, summary="Bulk update question status")
def bulk_update_status(
    payload: QuestionBulkStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Publisher")),
):
    repo = QuestionRepository(db)
    count = repo.bulk_update_status(payload.ids, payload.new_status)
    return {"updated_count": count, "new_status": payload.new_status.value}


@router.post("/bulk/import", response_model=QuestionBulkImportResponse, summary="Bulk import questions from JSON")
def bulk_import_questions(
    payload: QuestionBulkImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Faculty")),
):
    repo = QuestionRepository(db)
    created = 0
    skipped = 0
    errors = []

    for item in payload.items:
        try:
            if payload.skip_duplicates:
                existing = repo.check_duplicate(item.content)
                if existing:
                    skipped += 1
                    continue

            q_entity = Question(
                content=item.content,
                question_type=item.question_type,
                difficulty=item.difficulty,
                bloom_taxonomy=item.bloom_taxonomy,
                marks=item.marks,
                negative_marks=item.negative_marks,
                language=item.language,
                source=item.source,
                reference_book=item.reference_book,
                explanation=item.explanation,
                status=QuestionStatus.DRAFT,
                author_id=current_user.id,
            )
            db.add(q_entity)
            db.flush()

            for idx, opt in enumerate(item.options, start=1):
                opt_entity = QuestionOption(
                    question_id=q_entity.id,
                    content=opt.content,
                    option_index=opt.option_index or idx,
                    is_correct=opt.is_correct,
                    explanation=opt.explanation,
                )
                db.add(opt_entity)

            created += 1
        except Exception as e:
            errors.append(f"Content '{item.content[:30]}...': {str(e)}")

    db.commit()
    return QuestionBulkImportResponse(created=created, skipped=skipped, errors=errors)


# ─────────────────────── Search Questions List ──────────────────────────

@router.get("", response_model=QuestionListResponse, summary="Search & filter question bank")
def list_questions(
    q: Optional[str] = Query(default=None, description="Full-text search query"),
    subject_id: Optional[uuid.UUID] = Query(default=None),
    chapter_id: Optional[uuid.UUID] = Query(default=None),
    topic_id: Optional[uuid.UUID] = Query(default=None),
    subtopic_id: Optional[uuid.UUID] = Query(default=None),
    difficulty: Optional[DifficultyLevel] = Query(default=None),
    bloom_taxonomy: Optional[BloomTaxonomy] = Query(default=None),
    question_type: Optional[QuestionType] = Query(default=None),
    language: Optional[str] = Query(default=None),
    status: Optional[QuestionStatus] = Query(default=None),
    verification_status: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = QuestionRepository(db)
    result = repo.search(
        q=q, subject_id=subject_id, chapter_id=chapter_id, topic_id=topic_id,
        subtopic_id=subtopic_id, difficulty=difficulty, bloom_taxonomy=bloom_taxonomy,
        question_type=question_type, language=language, status=status,
        verification_status=verification_status, source=source, page=page, page_size=page_size
    )
    return QuestionListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
    )


# ─────────────────────── Create Question ─────────────────────────────────

@router.post("", response_model=QuestionResponse, status_code=http_status.HTTP_201_CREATED)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Faculty")),
):
    repo = QuestionRepository(db)

    # Check for duplicate
    dup = repo.check_duplicate(payload.content, payload.topic_id)
    if dup:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Duplicate question detected."
        )

    question = Question(
        content=payload.content,
        question_type=payload.question_type,
        difficulty=payload.difficulty,
        bloom_taxonomy=payload.bloom_taxonomy,
        marks=payload.marks,
        negative_marks=payload.negative_marks,
        language=payload.language,
        source=payload.source,
        reference_book=payload.reference_book,
        estimated_time_seconds=payload.estimated_time_seconds,
        verification_status=payload.verification_status,
        creation_source=payload.creation_source,
        explanation=payload.explanation,
        detailed_explanation=payload.detailed_explanation,
        quick_trick_explanation=payload.quick_trick_explanation,
        video_explanation_url=payload.video_explanation_url,
        subject_id=payload.subject_id,
        chapter_id=payload.chapter_id,
        topic_id=payload.topic_id,
        subtopic_id=payload.subtopic_id,
        learning_objective_id=payload.learning_objective_id,
        tags=payload.tags,
        ai_metadata=payload.ai_metadata,
        analytics_summary=payload.analytics_summary or {"attempt_count": 0, "correct_count": 0},
        status=QuestionStatus.DRAFT,
        author_id=current_user.id,
    )
    db.add(question)
    db.flush()

    for idx, opt in enumerate(payload.options, start=1):
        option_entity = QuestionOption(
            question_id=question.id,
            content=opt.content,
            option_index=opt.option_index or idx,
            is_correct=opt.is_correct,
            explanation=opt.explanation,
        )
        db.add(option_entity)

    db.commit()
    db.refresh(question)

    svc = QuestionWorkflowService(db)
    svc.create_revision(question, current_user.id, "Initial question creation")
    svc._audit(question, "CREATED", None, QuestionStatus.DRAFT, current_user.id)
    db.commit()

    logger.info(f"Created Question {question.id} by user {current_user.id}")
    return question


# ─────────────────────── Get Question by ID ───────────────────────────────

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = QuestionRepository(db)
    question = repo.get_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


# ─────────────────────── Update Question ─────────────────────────────────

@router.patch("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Editor")),
):
    repo = QuestionRepository(db)
    question = repo.get_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.status == QuestionStatus.PUBLISHED:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Published questions are immutable. Use POST /questions/{id}/spawn-draft to edit."
        )

    update_data = payload.model_dump(exclude_unset=True)
    if "options" in update_data:
        del update_data["options"]

    for field, value in update_data.items():
        setattr(question, field, value)

    db.commit()
    db.refresh(question)

    svc = QuestionWorkflowService(db)
    svc.create_revision(question, current_user.id, "Question update")
    svc._audit(question, "UPDATED", question.status, question.status, current_user.id)
    db.commit()

    logger.info(f"Updated Question {question_id} by user {current_user.id}")
    return question


# ─────────────────────── Workflow State Transitions ─────────────────────

@router.post("/{question_id}/transition", response_model=QuestionResponse)
def transition_question_workflow(
    question_id: uuid.UUID,
    payload: QuestionTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Reviewer")),
):
    svc = QuestionWorkflowService(db)
    try:
        updated = svc.transition(question_id, payload.new_status, current_user.id, payload.notes)
        return updated
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{question_id}/spawn-draft", response_model=QuestionResponse)
def spawn_draft_from_published(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Editor")),
):
    svc = QuestionWorkflowService(db)
    try:
        draft = svc.spawn_draft_from_published(question_id, current_user.id)
        return draft
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ─────────────────────── Soft Delete Question ────────────────────────────

@router.delete("/{question_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = QuestionRepository(db)
    question = repo.get_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.status == QuestionStatus.PUBLISHED:
        raise HTTPException(status_code=422, detail="Retire or archive before deleting published question.")

    repo.soft_delete(question_id)
    logger.info(f"Soft-deleted Question {question_id}")
    return None


# ─────────────────────── Revisions & Audit Logs ──────────────────────────

@router.get("/{question_id}/revisions", response_model=List[QuestionRevisionResponse])
def get_question_revisions(question_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = QuestionRevisionRepository(db)
    return repo.get_history(question_id)


@router.get("/{question_id}/audit-logs", response_model=List[QuestionAuditLogResponse])
def get_question_audit_logs(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Reviewer")),
):
    repo = QuestionAuditLogRepository(db)
    return repo.get_by_question(question_id)


# ─────────────────────── Reports Endpoint ────────────────────────────────

@router.post("/{question_id}/reports", response_model=QuestionReportResponse, status_code=http_status.HTTP_201_CREATED)
def report_question(
    question_id: uuid.UUID,
    payload: QuestionReportCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    repo = QuestionRepository(db)
    question = repo.get_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    report = QuestionReport(
        question_id=question_id,
        reporter_id=current_user.id if current_user else None,
        report_type=payload.report_type,
        description=payload.description,
        status="OPEN"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    logger.info(f"Created report for Question {question_id}")
    return report
