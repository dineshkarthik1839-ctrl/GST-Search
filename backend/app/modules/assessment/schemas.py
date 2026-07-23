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
    marks: float = 1.0
    negative_marks: float = 0.0
    explanation: Optional[str] = None
    language: str = "en"
    source: Optional[str] = None
    reference_book: Optional[str] = None


class QuestionBulkImportRequest(BaseModel):
    items: List[QuestionBulkImportItem] = Field(..., min_length=1, max_length=1000)
    skip_duplicates: bool = True


class QuestionBulkImportResponse(BaseModel):
    created: int
    skipped: int
    errors: List[str]


# ─────────────────────── Attempt & Test Session Schemas ───────────────────

class SaveAnswerRequest(BaseModel):
    selected_option_id: Optional[uuid.UUID] = None
    user_answer_text: Optional[str] = None
    status: str = Field(default="ANSWERED", description="ANSWERED, MARKED_FOR_REVIEW, ANSWERED_AND_MARKED, VISITED")
    time_spent_seconds: int = Field(default=0, ge=0)

class StartPracticeRequest(BaseModel):
    mode: str = Field(default="PRACTICE") # LEARNING, PRACTICE, TIMED_PRACTICE, WEAK_TOPIC_PRACTICE, etc.
    subject_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None
    num_questions: int = Field(default=10, ge=1, le=100)

class AttemptQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    selected_option_id: Optional[uuid.UUID] = None
    status: str
    is_correct: Optional[bool] = None
    marks_obtained: float
    time_spent_seconds: int
    question: Optional[QuestionResponse] = None

class AttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    mock_test_id: Optional[uuid.UUID] = None
    mode: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    time_taken_seconds: int
    score: float
    total_marks: float
    accuracy_pct: float
    speed_seconds_per_q: float
    correct_count: int
    wrong_count: int
    skipped_count: int
    attempt_questions: List[AttemptQuestionResponse] = Field(default_factory=list)

class ExamResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    attempt_id: uuid.UUID
    score: float
    percentile: float
    rank: int
    strengths_json: Optional[List[str]] = None
    weaknesses_json: Optional[List[str]] = None
    recommendations_json: Optional[List[str]] = None

class BookmarkToggleRequest(BaseModel):
    entity_type: str = Field(default="QUESTION", description="QUESTION, RESOURCE")
    entity_id: uuid.UUID

class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    created_at: datetime

