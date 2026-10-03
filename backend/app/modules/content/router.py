"""
Content Router - Full REST API for Enterprise CMS & Resource Library.
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

router = APIRouter(prefix="/content", tags=["CMS - Content & Resource Library"])


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


# ─────────────────────── Resource Library & Hub Static Routes ─────────────

@router.get("/library", summary="Unified Resource Library search")
def search_resource_library(
    content_type: Optional[ContentType] = Query(default=None),
    q: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.modules.content.services.resource_library import ResourceLibraryService
    svc = ResourceLibraryService(db)
    return svc.search_library(content_type=content_type, q=q, language=language, page=page, page_size=page_size)


@router.get("/library/continue-learning", summary="Get student continue learning list")
def get_continue_learning(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.content.services.resource_library import ResourceLibraryService
    from app.modules.assessment.router import _get_active_user_id
    svc = ResourceLibraryService(db)
    user_id = _get_active_user_id(db, current_user)
    items = svc.get_continue_learning(user_id=user_id)
    return [
        {
            "id": str(p.id),
            "content_item_id": str(p.content_item_id),
            "title": p.content_item.title if p.content_item else "Resource",
            "content_type": p.content_item.content_type.value if p.content_item else "PDF",
            "last_page_read": p.last_page_read,
            "video_timestamp_seconds": p.video_timestamp_seconds,
            "completion_pct": p.completion_pct,
            "last_accessed_at": p.last_accessed_at.isoformat() if p.last_accessed_at else None,
        }
        for p in items
    ]


@router.post("/library/{content_item_id}/progress", summary="Save continue learning progress")
def save_resource_progress(
    content_item_id: uuid.UUID,
    last_page_read: int = Query(default=1),
    video_timestamp_seconds: int = Query(default=0),
    completion_pct: float = Query(default=0.0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.content.services.resource_library import ResourceLibraryService
    from app.modules.assessment.router import _get_active_user_id
    svc = ResourceLibraryService(db)
    user_id = _get_active_user_id(db, current_user)
    progress = svc.save_progress(
        user_id=user_id,
        content_item_id=content_item_id,
        last_page_read=last_page_read,
        video_timestamp_seconds=video_timestamp_seconds,
        completion_pct=completion_pct,
    )
    return {"status": "SUCCESS", "progress_id": str(progress.id), "last_page_read": progress.last_page_read}


@router.post("/library/{content_item_id}/download", summary="Track offline resource download")
def track_resource_download(
    content_item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from app.modules.content.services.resource_library import ResourceLibraryService
    from app.modules.assessment.router import _get_active_user_id
    svc = ResourceLibraryService(db)
    user_id = _get_active_user_id(db, current_user)
    dl = svc.track_download(user_id=user_id, content_item_id=content_item_id)
    return {"status": "DOWNLOADED", "download_id": str(dl.id), "status_code": dl.download_status}


@router.post("/library/{content_item_id}/ai-chat", summary="Grounded AI Tutor response for resource")
def resource_ai_chat(
    content_item_id: uuid.UUID,
    query: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    from app.modules.content.services.resource_library import ResourceLibraryService
    svc = ResourceLibraryService(db)
    return svc.generate_ai_grounded_response(content_item_id=content_item_id, query=query)


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


@router.post("/bulk/status", response_model=dict, summary="Bulk update content status")
def bulk_update_status(
    payload: BulkStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Publisher")),
):
    repo = ContentRepository(db)
    count = repo.bulk_update_status(payload.ids, payload.new_status)
    return {"updated_count": count, "new_status": payload.new_status.value}


@router.post("/bulk/import", response_model=BulkImportResponse, summary="Bulk import content items")
def bulk_import_items(
    payload: BulkImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Faculty")),
):
    repo = ContentRepository(db)
    created = 0
    skipped = 0
    errors = []

    for item in payload.items:
        try:
            slug = item.slug or _auto_slug(item.title)
            if payload.skip_duplicates:
                existing = repo.get_by_slug(slug)
                if not existing:
                    from sqlalchemy import select, func
                    existing = db.execute(
                        select(ContentItem).filter(
                            func.lower(ContentItem.title) == item.title.lower(),
                            ContentItem.is_deleted == False
                        )
                    ).scalars().first()

                if existing:
                    skipped += 1
                    continue

            new_entity = ContentItem(
                title=item.title,
                slug=slug,
                description=item.description,
                content_type=item.content_type,
                status=ContentStatus.DRAFT,
                language=item.language,
                author_id=current_user.id,
            )
            db.add(new_entity)
            db.flush()
            _apply_extension(db, new_entity, item)
            created += 1
        except Exception as e:
            errors.append(f"Title '{item.title}': {str(e)}")

    db.commit()
    return BulkImportResponse(created=created, skipped=skipped, errors=errors)


# ─────────────────────── Search Content Items ────────────────────────────

@router.get("", response_model=ContentItemListResponse, summary="Search & filter content items")
def list_content(
    q: Optional[str] = Query(default=None, description="Full-text search query"),
    content_type: Optional[ContentType] = Query(default=None),
    status: Optional[ContentStatus] = Query(default=None),
    language: Optional[str] = Query(default=None),
    author_id: Optional[uuid.UUID] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = ContentRepository(db)
    result = repo.search(
        q=q, content_type=content_type, status=status,
        language=language, author_id=author_id, page=page, page_size=page_size
    )
    return ContentItemListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


# ─────────────────────── Create Content Item ────────────────────────────

@router.post("", response_model=ContentItemResponse, status_code=http_status.HTTP_201_CREATED)
def create_content(
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Faculty")),
):
    repo = ContentRepository(db)
    slug = payload.slug or _auto_slug(payload.title)

    if repo.get_by_slug(slug):
        raise HTTPException(status_code=409, detail=f"Slug '{slug}' already exists.")

    item = ContentItem(
        title=payload.title,
        slug=slug,
        description=payload.description,
        content_type=payload.content_type,
        status=ContentStatus.DRAFT,
        thumbnail_url=payload.thumbnail_url,
        language=payload.language,
        publish_date=payload.publish_date,
        expiry_date=payload.expiry_date,
        metadata_json=payload.metadata_json,
        author_id=current_user.id,
    )
    db.add(item)
    db.flush()

    _apply_extension(db, item, payload)
    db.commit()
    db.refresh(item)

    svc = ContentWorkflowService(db)
    svc._create_revision(item, current_user.id, "Initial creation")
    svc._audit(item, "CREATED", None, ContentStatus.DRAFT, current_user.id)
    db.commit()

    logger.info(f"Created ContentItem {item.id} ({item.slug}) by user {current_user.id}")
    return item


# ─────────────────────── Get by ID / Slug ────────────────────────────────

@router.get("/slug/{slug}", response_model=ContentItemResponse)
def get_content_by_slug(slug: str, db: Session = Depends(get_db)):
    repo = ContentRepository(db)
    item = repo.get_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return item


@router.get("/{content_id}", response_model=ContentItemResponse)
def get_content(content_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = ContentRepository(db)
    item = repo.get_by_id(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return item


# ─────────────────────── Update Content Item ────────────────────────────

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
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PUBLISHED items are immutable. Spawn a new draft first."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if not field.endswith("_details"):
            setattr(item, field, value)

    _apply_extension(db, item, payload)
    db.commit()
    db.refresh(item)

    svc = ContentWorkflowService(db)
    svc._create_revision(item, current_user.id, "Content update")
    svc._audit(item, "UPDATED", item.status, item.status, current_user.id)
    db.commit()

    logger.info(f"Updated ContentItem {content_id} by user {current_user.id}")
    return item


# ─────────────────────── Workflow Transitions ────────────────────────────

@router.post("/{content_id}/transition", response_model=ContentItemResponse)
def transition_content_workflow(
    content_id: uuid.UUID,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Reviewer")),
):
    svc = ContentWorkflowService(db)
    try:
        updated = svc.transition(content_id, payload.new_status, current_user.id, payload.notes)
        return updated
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{content_id}/spawn-draft", response_model=ContentItemResponse)
def spawn_draft_from_published(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Editor")),
):
    svc = ContentWorkflowService(db)
    try:
        draft = svc.spawn_draft_from_published(content_id, current_user.id)
        return draft
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ─────────────────────── Soft Delete Content Item ────────────────────────

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
        raise HTTPException(status_code=422, detail="Archive published content before deletion.")

    repo.soft_delete(content_id)
    logger.info(f"Soft-deleted ContentItem {content_id}")
    return None


# ─────────────────────── Revisions & Audit Logs ──────────────────────────

@router.get("/{content_id}/revisions", response_model=List[ContentRevisionResponse])
def get_revisions(content_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = ContentRevisionRepository(db)
    return repo.get_history(content_id)


@router.get("/{content_id}/audit-logs", response_model=List[ContentAuditLogResponse])
def get_audit_logs(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Reviewer")),
):
    repo = ContentAuditLogRepository(db)
    return repo.get_by_content(content_id)
