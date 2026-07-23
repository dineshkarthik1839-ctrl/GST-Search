import uuid
import csv
import io
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_optional, RequireRole
from app.modules.users.models import User
from app.modules.assessment.models import (
    Question, QuestionOption, QuestionStatus, QuestionType,
    DifficultyLevel, BloomTaxonomy, QuestionReport
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
    QuestionBulkImportRequest, QuestionBulkImportResponse
)
from app.core.logger import logger
from app.core.exceptions import AppException

router = APIRouter(prefix="/questions", tags=["Question Bank Engine"])


# ─────────────────────── Search & List ───────────────────────────────────

@router.get("", response_model=QuestionListResponse, summary="Search & filter question bank")
def list_questions(
    q: Optional[str] = Query(default=None, description="Full-text search on content/explanation"),
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
    published_only: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    repo = QuestionRepository(db)
    return repo.search(
        q=q,
        subject_id=subject_id,
        chapter_id=chapter_id,
        topic_id=topic_id,
        subtopic_id=subtopic_id,
        difficulty=difficulty,
        bloom_taxonomy=bloom_taxonomy,
        question_type=question_type,
        language=language,
        status=status,
        verification_status=verification_status,
        source=source,
        published_only=published_only,
        skip=skip,
        limit=limit,
    )


# ─────────────────────── Create Question ─────────────────────────────────

@router.post("", response_model=QuestionResponse, status_code=http_status.HTTP_201_CREATED)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Faculty")),
):
    repo = QuestionRepository(db)

    # Check for duplicate content
    if repo.check_duplicate(payload.content, payload.topic_id):
        raise HTTPException(
            status_code=409,
            detail="Duplicate question detected with identical text under the same topic.",
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

    # Initial Revision & Audit Log
    svc = QuestionWorkflowService(db)
    svc.create_revision(question, current_user.id, "Initial question creation")
    svc._audit(question, "CREATED", None, QuestionStatus.DRAFT, current_user.id)
    db.commit()

    logger.info(f"Created Question {question.id} by user {current_user.id}")
    return question


# ─────────────────────── Get Question ────────────────────────────────────

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
            status_code=422,
            detail="Cannot edit PUBLISHED question directly. Use /spawn-draft to create a new draft version.",
        )

    update_data = payload.model_dump(exclude_none=True, exclude={"options"})
    for field, value in update_data.items():
        setattr(question, field, value)
    question.updated_at = datetime.now(timezone.utc)

    if payload.options is not None:
        # Replace options
        for existing_opt in question.options:
            db.delete(existing_opt)
        db.flush()

        for idx, opt in enumerate(payload.options, start=1):
            new_opt = QuestionOption(
                question_id=question.id,
                content=opt.content,
                option_index=opt.option_index or idx,
                is_correct=opt.is_correct,
                explanation=opt.explanation,
            )
            db.add(new_opt)

    db.commit()
    db.refresh(question)
    logger.info(f"Updated Question {question.id}")
    return question


# ─────────────────────── Workflow Transition ─────────────────────────────

@router.post("/{question_id}/transition", response_model=QuestionResponse)
def transition_question(
    question_id: uuid.UUID,
    payload: QuestionTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Reviewer")),
):
    svc = QuestionWorkflowService(db)
    try:
        question = svc.transition(
            question_id=question_id,
            new_status=payload.new_status,
            performed_by_id=current_user.id,
            notes=payload.notes,
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return question


# ─────────────────────── Spawn Draft from Published ──────────────────────

@router.post("/{question_id}/spawn-draft", response_model=QuestionResponse)
def spawn_draft(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Editor")),
):
    svc = QuestionWorkflowService(db)
    try:
        draft = svc.spawn_draft_from_published(question_id, current_user.id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return draft


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
        status="OPEN",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    logger.info(f"User reported Question {question_id}: {payload.report_type}")
    return report


# ─────────────────────── Bulk Operations ─────────────────────────────────

@router.post("/bulk/status", summary="Bulk update question status")
def bulk_update_question_status(
    payload: QuestionBulkStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = QuestionRepository(db)
    count = repo.bulk_update_status(payload.ids, payload.new_status)
    return {"updated": count}


@router.post("/bulk/import", response_model=QuestionBulkImportResponse, summary="Bulk import questions")
def bulk_import_questions(
    payload: QuestionBulkImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = QuestionRepository(db)
    created = 0
    skipped = 0
    errors: List[str] = []

    for item in payload.items:
        try:
            if payload.skip_duplicates and repo.check_duplicate(item.content):
                skipped += 1
                continue

            q_entity = Question(
                content=item.content,
                question_type=item.question_type,
                difficulty=item.difficulty,
                bloom_taxonomy=item.bloom_taxonomy,
                explanation=item.explanation,
                language=item.language,
                source=item.source,
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


# ─────────────────────── Export ──────────────────────────────────────────

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
