from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.assessment.models import (
    QuestionType, DifficultyLevel, BloomTaxonomy, QuestionStatus
)


# ─────────────────────── Question Option Schemas ──────────────────────────

class QuestionOptionBase(BaseModel):
    content: str
    option_index: int = 1
    is_correct: bool = False
    explanation: Optional[str] = None

class QuestionOptionCreate(QuestionOptionBase):
    pass

class QuestionOptionResponse(QuestionOptionBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID


# ─────────────────────── Question Core Schemas ────────────────────────────

class QuestionBase(BaseModel):
    content: str = Field(..., min_length=1)
    question_type: QuestionType = QuestionType.MCQ
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    bloom_taxonomy: Optional[BloomTaxonomy] = BloomTaxonomy.UNDERSTAND
    marks: float = 1.0
    negative_marks: float = 0.25
    language: str = Field(default="en", max_length=50)
    source: Optional[str] = None
    reference_book: Optional[str] = None
    estimated_time_seconds: int = 60
    verification_status: str = "UNVERIFIED"
    creation_source: str = "HUMAN_GENERATED"
    
    explanation: Optional[str] = None
    detailed_explanation: Optional[str] = None
    quick_trick_explanation: Optional[str] = None
    video_explanation_url: Optional[str] = None
    
    subject_id: Optional[uuid.UUID] = None
    chapter_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None
    subtopic_id: Optional[uuid.UUID] = None
    learning_objective_id: Optional[uuid.UUID] = None
    
    tags: Optional[Dict[str, Any]] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    analytics_summary: Optional[Dict[str, Any]] = None


class QuestionCreate(QuestionBase):
    options: List[QuestionOptionCreate] = Field(default_factory=list)


class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    question_type: Optional[QuestionType] = None
    difficulty: Optional[DifficultyLevel] = None
    bloom_taxonomy: Optional[BloomTaxonomy] = None
    marks: Optional[float] = None
    negative_marks: Optional[float] = None
    language: Optional[str] = None
    source: Optional[str] = None
    reference_book: Optional[str] = None
    estimated_time_seconds: Optional[int] = None
    explanation: Optional[str] = None
    detailed_explanation: Optional[str] = None
    quick_trick_explanation: Optional[str] = None
    video_explanation_url: Optional[str] = None
    options: Optional[List[QuestionOptionCreate]] = None
    tags: Optional[Dict[str, Any]] = None
    ai_metadata: Optional[Dict[str, Any]] = None


class QuestionResponse(QuestionBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: QuestionStatus
    version: int
    author_id: Optional[uuid.UUID] = None
    options: List[QuestionOptionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class QuestionListResponse(BaseModel):
    items: List[QuestionResponse]
    total: int
    page: int
    size: int


# ─────────────────────── Revisions & Audit Schemas ───────────────────────

class QuestionRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    version_number: int
    snapshot: Dict[str, Any]
    created_by_id: Optional[uuid.UUID] = None
    change_summary: Optional[str] = None
    created_at: datetime


class QuestionAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    action: str
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    performed_by_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    created_at: datetime


# ─────────────────────── Reporting & Workflows ───────────────────────────

class QuestionReportCreate(BaseModel):
    report_type: str = Field(..., description="WRONG_ANSWER, TYPO, UNCLEAR_EXPLANATION, OTHER")
    description: str = Field(..., min_length=5)


class QuestionReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    reporter_id: Optional[uuid.UUID] = None
    report_type: str
    description: str
    status: str
    created_at: datetime


class QuestionTransitionRequest(BaseModel):
    new_status: QuestionStatus
    notes: Optional[str] = Field(default=None, max_length=500)


class QuestionBulkStatusRequest(BaseModel):
    ids: List[uuid.UUID] = Field(..., min_length=1, max_length=100)
    new_status: QuestionStatus


class QuestionBulkImportItem(BaseModel):
    content: str
    options: List[QuestionOptionCreate]
    question_type: QuestionType = QuestionType.MCQ
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    bloom_taxonomy: Optional[BloomTaxonomy] = BloomTaxonomy.UNDERSTAND
    explanation: Optional[str] = None
    language: str = "en"
    source: Optional[str] = None


class QuestionBulkImportRequest(BaseModel):
    items: List[QuestionBulkImportItem] = Field(..., min_length=1, max_length=1000)
    skip_duplicates: bool = True


class QuestionBulkImportResponse(BaseModel):
    created: int
    skipped: int
    errors: List[str]
