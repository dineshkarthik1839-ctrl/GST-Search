import uuid
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base_class import BaseEntity
import enum

class ContentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEW = "REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class ContentType(str, enum.Enum):
    BOOK = "BOOK"
    VIDEO = "VIDEO"
    NOTE = "NOTE"
    PDF = "PDF"
    MIND_MAP = "MIND_MAP"
    FLASH_CARD = "FLASH_CARD"
    FORMULA_SHEET = "FORMULA_SHEET"
    QUESTION_BANK = "QUESTION_BANK"
    CURRENT_AFFAIR = "CURRENT_AFFAIR"
    PREVIOUS_PAPER = "PREVIOUS_PAPER"
    MOCK_TEST = "MOCK_TEST"

class ContentItem(BaseEntity):
    __tablename__ = "content_items"
    
    title: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), index=True)
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus), default=ContentStatus.DRAFT, index=True)
    # NOTE: version is inherited from BaseEntity (optimistic locking)

    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    language: Mapped[str] = mapped_column(String(50), default="en")

    publish_date: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), index=True)
    expiry_date: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), index=True)

    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB) # For AI metadata, search metadata, cloud storage metadata

    
    # Base Relationships
    author = relationship("User", lazy="selectin")
    
    # Extension Relationships (1:1)
    video_details: Mapped[Optional["VideoDetails"]] = relationship("VideoDetails", back_populates="content_item", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    book_details: Mapped[Optional["BookDetails"]] = relationship("BookDetails", back_populates="content_item", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    pdf_details: Mapped[Optional["PdfDetails"]] = relationship("PdfDetails", back_populates="content_item", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    quiz_details: Mapped[Optional["QuizDetails"]] = relationship("QuizDetails", back_populates="content_item", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    flashcard_details: Mapped[Optional["FlashCardDetails"]] = relationship("FlashCardDetails", back_populates="content_item", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    mindmap_details: Mapped[Optional["MindMapDetails"]] = relationship("MindMapDetails", back_populates="content_item", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    
    # Workflow
    revisions: Mapped[List["ContentRevision"]] = relationship("ContentRevision", back_populates="content_item", cascade="all, delete-orphan", lazy="selectin")
    audit_logs: Mapped[List["ContentAuditLog"]] = relationship("ContentAuditLog", back_populates="content_item", cascade="all, delete-orphan", lazy="selectin")
    
    # Legacy Relationships (Resource mapped to ContentItem now)
    resources: Mapped[List["Resource"]] = relationship("Resource", back_populates="content_item", cascade="all, delete-orphan", lazy="selectin")
    exam_mappings: Mapped[List["ExamCurrentAffair"]] = relationship("ExamCurrentAffair", back_populates="content_item", cascade="all, delete-orphan", lazy="selectin")

# --- Extension Tables ---

class VideoDetails(BaseEntity):
    __tablename__ = "content_video_details"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), unique=True, index=True)
    video_url: Mapped[str] = mapped_column(String(500))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    transcript: Mapped[Optional[str]] = mapped_column(Text)
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="video_details")

class BookDetails(BaseEntity):
    __tablename__ = "content_book_details"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), unique=True, index=True)
    author_name: Mapped[Optional[str]] = mapped_column(String(255))
    isbn: Mapped[Optional[str]] = mapped_column(String(50))
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    publisher: Mapped[Optional[str]] = mapped_column(String(255))
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="book_details")

class PdfDetails(BaseEntity):
    __tablename__ = "content_pdf_details"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), unique=True, index=True)
    pdf_url: Mapped[str] = mapped_column(String(500))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="pdf_details")

class QuizDetails(BaseEntity):
    __tablename__ = "content_quiz_details"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), unique=True, index=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    passing_score: Mapped[Float] = mapped_column(Float, default=0.0)
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="quiz_details")

class FlashCardDetails(BaseEntity):
    __tablename__ = "content_flashcard_details"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), unique=True, index=True)
    deck_size: Mapped[int] = mapped_column(Integer, default=0)
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="flashcard_details")

class MindMapDetails(BaseEntity):
    __tablename__ = "content_mindmap_details"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), unique=True, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    interactive_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="mindmap_details")

# --- Versioning and Workflow ---

class ContentRevision(BaseEntity):
    __tablename__ = "content_revisions"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    snapshot: Mapped[dict] = mapped_column(JSONB)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    change_summary: Mapped[Optional[str]] = mapped_column(String(500))
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="revisions")

class ContentAuditLog(BaseEntity):
    __tablename__ = "content_audit_logs"
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(100)) # e.g. STATUS_CHANGED, CREATED
    old_status: Mapped[Optional[str]] = mapped_column(String(50))
    new_status: Mapped[Optional[str]] = mapped_column(String(50))
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[Optional[str]] = mapped_column(String(500))
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="audit_logs")

# --- Legacy Mappings Adapted ---

class Resource(BaseEntity):
    """
    Connects an academic Topic to a ContentItem.
    """
    __tablename__ = "resources"
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), index=True)
    
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="resources", lazy="selectin")

class ExamCurrentAffair(BaseEntity):
    __tablename__ = "exam_current_affairs"
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), index=True)
    
    exam = relationship("Exam", back_populates="current_affairs", lazy="selectin")
    content_item: Mapped["ContentItem"] = relationship("ContentItem", back_populates="exam_mappings", lazy="selectin")
