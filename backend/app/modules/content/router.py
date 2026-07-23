"""
Content Router - Full REST API for Enterprise CMS.
Endpoints: CRUD, Workflow, Revisions, Audit Logs, Bulk Operations, Import/Export.
"""
import uuid
import csv
import io
import re
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_optional, RequireRole
from app.modules.users.models import User
from app.modules.content.models import (
    ContentItem, ContentType, ContentStatus,
    VideoDetails, BookDetails, PdfDetails,
    QuizDetails, FlashCardDetails, MindMapDetails,
)
from app.modules.content.repository import (
    ContentRepository, ContentRevisionRepository, ContentAuditLogRepository
)
from app.modules.content.service import ContentWorkflowService
from app.modules.content.schemas import (
    ContentItemCreate, ContentItemUpdate, ContentItemResponse,
    ContentItemListResponse, ContentRevisionResponse,
    ContentAuditLogResponse, TransitionRequest,
    BulkStatusRequest, BulkImportRequest, BulkImportResponse,
)
from app.core.logger import logger
from app.core.exceptions import AppException

router = APIRouter(prefix="/content", tags=["CMS - Content"])


def _auto_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug


def _apply_extension(db: Session, item: ContentItem, data: ContentItemCreate | ContentItemUpdate):
    """Create or update 1:1 extension detail rows."""
    if data.video_details:
        ext = VideoDetails(content_item_id=item.id, **data.video_details.model_dump())
        db.merge(ext)
    if data.book_details:
        ext = BookDetails(content_item_id=item.id, **data.book_details.model_dump())
        db.merge(ext)
    if data.pdf_details:
        ext = PdfDetails(content_item_id=item.id, **data.pdf_details.model_dump())
        db.merge(ext)
    if data.quiz_details:
        ext = QuizDetails(content_item_id=item.id, **data.quiz_details.model_dump())
        db.merge(ext)
    if data.flashcard_details:
        ext = FlashCardDetails(content_item_id=item.id, **data.flashcard_details.model_dump())
        db.merge(ext)
    if data.mindmap_details:
        ext = MindMapDetails(content_item_id=item.id, **data.mindmap_details.model_dump())
        db.merge(ext)
    db.commit()


# ─────────────────────── List & Search ───────────────────────────────────

@router.get("", response_model=ContentItemListResponse, summary="Search & list content")
def list_content(
    q: Optional[str] = Query(default=None, description="Full-text search on title/description"),
    content_type: Optional[ContentType] = Query(default=None),
    status: Optional[ContentStatus] = Query(default=None),
    language: Optional[str] = Query(default=None),
    published_only: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    repo = ContentRepository(db)
    return repo.search(
        q=q,
        content_type=content_type,
        status=status,
        language=language,
        published_only=published_only,
        skip=skip,
        limit=limit,
    )


# ─────────────────────── Create ──────────────────────────────────────────

@router.post("", response_model=ContentItemResponse, status_code=http_status.HTTP_201_CREATED)
def create_content(
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Faculty")),
):
    repo = ContentRepository(db)

    # Auto-generate slug if not provided
    slug = payload.slug or _auto_slug(payload.title)

    # Ensure slug is unique
    if repo.get_by_slug(slug):
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    item = ContentItem(
        title=payload.title,
        slug=slug,
        description=payload.description,
        content_type=payload.content_type,
        status=ContentStatus.DRAFT,
        author_id=current_user.id,
        language=payload.language,
        thumbnail_url=payload.thumbnail_url,
        publish_date=payload.publish_date,
        expiry_date=payload.expiry_date,
        metadata_json=payload.metadata_json,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    _apply_extension(db, item, payload)
    db.refresh(item)

    # Create initial revision
    svc = ContentWorkflowService(db)
    svc._create_revision(item, current_user.id, "Initial creation")
    svc._audit(item, "CREATED", None, ContentStatus.DRAFT, current_user.id)
    db.commit()

    logger.info(f"Created ContentItem {item.id} ({item.slug}) by user {current_user.id}")
    return item


# ─────────────────────── Get by ID / Slug ────────────────────────────────

@router.get("/{content_id}", response_model=ContentItemResponse)
def get_content(content_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = ContentRepository(db)
    item = repo.get_by_id(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return item


@router.get("/slug/{slug}", response_model=ContentItemResponse)
def get_content_by_slug(slug: str, db: Session = Depends(get_db)):
    repo = ContentRepository(db)
    item = repo.get_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return item


# ─────────────────────── Update ──────────────────────────────────────────

@router.patch("/{content_id}", response_model=ContentItemResponse)
def update_content(
    content_id: uuid.UUID,
    payload: ContentItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Editor")),
):
    repo = ContentRepository(db)
    item = repo.get_by_id(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    if item.status == ContentStatus.PUBLISHED:
        raise HTTPException(
            status_code=422,
            detail="Cannot edit PUBLISHED content. Use /spawn-draft to create a new version.",
        )

    update_data = payload.model_dump(exclude_none=True, exclude={"video_details", "book_details", "pdf_details", "quiz_details", "flashcard_details", "mindmap_details"})
    for field, value in update_data.items():
        setattr(item, field, value)
    item.updated_at = datetime.now(timezone.utc)

    _apply_extension(db, item, payload)
    db.commit()
    db.refresh(item)
    logger.info(f"Updated ContentItem {item.id}")
    return item


# ─────────────────────── Workflow Transition ─────────────────────────────

@router.post("/{content_id}/transition", response_model=ContentItemResponse, summary="Change content status")
def transition_content(
    content_id: uuid.UUID,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Reviewer")),
):
    svc = ContentWorkflowService(db)
    try:
        item = svc.transition(
            content_id=content_id,
            new_status=payload.new_status,
            performed_by_id=current_user.id,
            notes=payload.notes,
            publish_date=payload.publish_date,
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return item


# ─────────────────────── Spawn Draft from Published ──────────────────────

@router.post("/{content_id}/spawn-draft", response_model=ContentItemResponse, summary="Clone published content as new draft")
def spawn_draft(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Editor")),
):
    svc = ContentWorkflowService(db)
    try:
        draft = svc.spawn_draft_from_published(content_id, current_user.id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return draft


# ─────────────────────── Soft Delete ─────────────────────────────────────

@router.delete("/{content_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = ContentRepository(db)
    item = repo.get_by_id(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    if item.status == ContentStatus.PUBLISHED:
        raise HTTPException(status_code=422, detail="Archive before deleting published content.")

    repo.soft_delete(content_id)
    logger.info(f"Soft-deleted ContentItem {content_id}")
    return None


# ─────────────────────── Revision History ────────────────────────────────

@router.get("/{content_id}/revisions", response_model=List[ContentRevisionResponse])
def get_revisions(content_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = ContentRevisionRepository(db)
    return repo.get_history(content_id)


# ─────────────────────── Audit Logs ──────────────────────────────────────

@router.get("/{content_id}/audit-logs", response_model=List[ContentAuditLogResponse])
def get_audit_logs(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Reviewer")),
):
    repo = ContentAuditLogRepository(db)
    return repo.get_by_content_item(content_id)


# ─────────────────────── Bulk Operations ─────────────────────────────────

@router.post("/bulk/status", summary="Bulk update content status")
def bulk_update_status(
    payload: BulkStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = ContentRepository(db)
    count = repo.bulk_update_status(payload.ids, payload.new_status)
    return {"updated": count}


@router.post("/bulk/import", response_model=BulkImportResponse, summary="Bulk import content items")
def bulk_import(
    payload: BulkImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = ContentRepository(db)
    created = 0
    skipped = 0
    errors: List[str] = []

    for item_data in payload.items:
        try:
            if payload.skip_duplicates and repo.check_duplicate(item_data.title, item_data.content_type):
                skipped += 1
                continue

            slug = _auto_slug(item_data.title)
            if repo.get_by_slug(slug):
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"

            item = ContentItem(
                title=item_data.title,
                slug=slug,
                description=item_data.description,
                content_type=item_data.content_type,
                status=ContentStatus.DRAFT,
                version=1,
                author_id=current_user.id,
                language=item_data.language,
            )
            db.add(item)
            db.flush()  # get id without full commit
            created += 1
        except Exception as e:
            errors.append(f"Row '{item_data.title}': {str(e)}")

    db.commit()
    return BulkImportResponse(created=created, skipped=skipped, errors=errors)


# ─────────────────────── Export ──────────────────────────────────────────

@router.get("/export/csv", summary="Export content list as CSV")
def export_csv(
    content_type: Optional[ContentType] = Query(default=None),
    status: Optional[ContentStatus] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin")),
):
    repo = ContentRepository(db)
    result = repo.search(content_type=content_type, status=status, limit=10000)
    items = result["items"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "slug", "content_type", "status", "language", "version", "created_at"])
    for item in items:
        writer.writerow([
            str(item.id), item.title, item.slug,
            item.content_type.value, item.status.value,
            item.language, item.version, item.created_at.isoformat()
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=content_export.csv"},
    )
