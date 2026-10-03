"""
Content Pydantic v2 Schemas - Full OpenAPI coverage.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

from app.modules.content.models import ContentType, ContentStatus


# ─────────────────────── Extension Detail Schemas ────────────────────────

class VideoDetailsBase(BaseModel):
    video_url: str
    duration_seconds: int = 0
    transcript: Optional[str] = None

class VideoDetailsCreate(VideoDetailsBase):
    pass

class VideoDetailsResponse(VideoDetailsBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class BookDetailsBase(BaseModel):
    author_name: Optional[str] = None
    isbn: Optional[str] = None
    page_count: Optional[int] = None
    publisher: Optional[str] = None

class BookDetailsCreate(BookDetailsBase):
    pass

class BookDetailsResponse(BookDetailsBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class PdfDetailsBase(BaseModel):
    pdf_url: str
    file_size_bytes: Optional[int] = None

class PdfDetailsCreate(PdfDetailsBase):
    pass

class PdfDetailsResponse(PdfDetailsBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class QuizDetailsBase(BaseModel):
    total_questions: int = 0
    passing_score: float = 0.0

class QuizDetailsCreate(QuizDetailsBase):
    pass

class QuizDetailsResponse(QuizDetailsBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class FlashCardDetailsBase(BaseModel):
    deck_size: int = 0

class FlashCardDetailsCreate(FlashCardDetailsBase):
    pass

class FlashCardDetailsResponse(FlashCardDetailsBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class MindMapDetailsBase(BaseModel):
    image_url: Optional[str] = None
    interactive_url: Optional[str] = None

class MindMapDetailsCreate(MindMapDetailsBase):
    pass

class MindMapDetailsResponse(MindMapDetailsBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


# ──────────────────────── ContentItem Schemas ─────────────────────────────

class ContentItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: ContentType
    thumbnail_url: Optional[str] = None
    language: str = Field(default="en", max_length=50)
    publish_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ContentItemCreate(ContentItemBase):
    slug: Optional[str] = Field(default=None, max_length=255)
    video_details: Optional[VideoDetailsCreate] = None
    book_details: Optional[BookDetailsCreate] = None
    pdf_details: Optional[PdfDetailsCreate] = None
    quiz_details: Optional[QuizDetailsCreate] = None
    flashcard_details: Optional[FlashCardDetailsCreate] = None
    mindmap_details: Optional[MindMapDetailsCreate] = None

    @field_validator("slug", mode="before")
    @classmethod
    def auto_slug(cls, v, info):
        if v:
            return re.sub(r"[^a-z0-9-]", "-", v.lower())
        return None


class ContentItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    language: Optional[str] = Field(default=None, max_length=50)
    publish_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    metadata_json: Optional[Dict[str, Any]] = None
    video_details: Optional[VideoDetailsCreate] = None
    book_details: Optional[BookDetailsCreate] = None
    pdf_details: Optional[PdfDetailsCreate] = None
    quiz_details: Optional[QuizDetailsCreate] = None
    flashcard_details: Optional[FlashCardDetailsCreate] = None
    mindmap_details: Optional[MindMapDetailsCreate] = None


class ContentItemResponse(ContentItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    slug: str
    status: ContentStatus
    version: int
    author_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    video_details: Optional[VideoDetailsResponse] = None
    book_details: Optional[BookDetailsResponse] = None
    pdf_details: Optional[PdfDetailsResponse] = None
    quiz_details: Optional[QuizDetailsResponse] = None
    flashcard_details: Optional[FlashCardDetailsResponse] = None
    mindmap_details: Optional[MindMapDetailsResponse] = None


class ContentItemListResponse(BaseModel):
    items: List[ContentItemResponse]
    total: int
    page: int
    size: int
    page_size: int = 20
    total_pages: int = 1


# ─────────────────────── Revision & Audit Schemas ────────────────────────

class ContentRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    content_item_id: uuid.UUID
    version_number: int
    snapshot: Dict[str, Any]
    created_by_id: Optional[uuid.UUID] = None
    change_summary: Optional[str] = None
    created_at: datetime


class ContentAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    content_item_id: uuid.UUID
    action: str
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    performed_by_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    created_at: datetime


# ─────────────────────── Workflow Schemas ────────────────────────────────

class TransitionRequest(BaseModel):
    new_status: ContentStatus
    notes: Optional[str] = Field(default=None, max_length=500)
    publish_date: Optional[datetime] = None


class BulkStatusRequest(BaseModel):
    ids: List[uuid.UUID] = Field(..., min_length=1, max_length=100)
    new_status: ContentStatus


class BulkImportItem(BaseModel):
    title: str
    content_type: ContentType
    description: Optional[str] = None
    language: str = "en"


class BulkImportRequest(BaseModel):
    items: List[BulkImportItem] = Field(..., min_length=1, max_length=500)
    skip_duplicates: bool = True


class BulkImportResponse(BaseModel):
    created: int
    skipped: int
    errors: List[str]
