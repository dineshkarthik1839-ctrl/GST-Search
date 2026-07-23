import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Enum, Text, Float, Boolean, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base_class import BaseEntity
import enum

class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    MULTI_SELECT = "MULTI_SELECT"
    NUMERICAL = "NUMERICAL"
    MATCH_FOLLOWING = "MATCH_FOLLOWING"
    ASSERTION_REASON = "ASSERTION_REASON"
    SUBJECTIVE = "SUBJECTIVE"
    TRUE_FALSE = "TRUE_FALSE"

class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class BloomTaxonomy(str, enum.Enum):
    REMEMBER = "REMEMBER"
    UNDERSTAND = "UNDERSTAND"
    APPLY = "APPLY"
    ANALYZE = "ANALYZE"
    EVALUATE = "EVALUATE"
    CREATE = "CREATE"

class QuestionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEW = "REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    RETIRED = "RETIRED"
    ARCHIVED = "ARCHIVED"

class Question(BaseEntity):
    __tablename__ = "questions"
    
    # Hierarchy Mapping
    subject_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subjects.id", ondelete="SET NULL"), index=True)
    chapter_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("chapters.id", ondelete="SET NULL"), index=True)
    topic_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), index=True)
    subtopic_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subtopics.id", ondelete="SET NULL"), index=True)
    learning_objective_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("learning_objectives.id", ondelete="SET NULL"), index=True)
    
    # Core Content (Rich Text / LaTeX / Markdown)
    content: Mapped[str] = mapped_column(Text)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), default=QuestionType.MCQ, index=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM, index=True)
    bloom_taxonomy: Mapped[Optional[BloomTaxonomy]] = mapped_column(Enum(BloomTaxonomy), default=BloomTaxonomy.UNDERSTAND, index=True)
    
    marks: Mapped[float] = mapped_column(Float, default=1.0)
    negative_marks: Mapped[float] = mapped_column(Float, default=0.25)
    language: Mapped[str] = mapped_column(String(50), default="en", index=True)
    
    source: Mapped[Optional[str]] = mapped_column(String(255))
    reference_book: Mapped[Optional[str]] = mapped_column(String(255))
    estimated_time_seconds: Mapped[int] = mapped_column(Integer, default=60)
    
    # Workflow & Audit Status
    status: Mapped[QuestionStatus] = mapped_column(Enum(QuestionStatus), default=QuestionStatus.DRAFT, index=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED", index=True) # VERIFIED, UNVERIFIED
    creation_source: Mapped[str] = mapped_column(String(50), default="HUMAN_GENERATED", index=True) # HUMAN_GENERATED, AI_GENERATED
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    
    # Multi-level Explanations
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    detailed_explanation: Mapped[Optional[str]] = mapped_column(Text)
    quick_trick_explanation: Mapped[Optional[str]] = mapped_column(Text)
    video_explanation_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # AI & Semantic Search Metadata
    tags: Mapped[Optional[dict]] = mapped_column(JSONB) # list of tags
    ai_metadata: Mapped[Optional[dict]] = mapped_column(JSONB) # {embedding_status, vector_id, difficulty_predicted, ai_quality_score, ai_review_status, ai_suggested_edits}
    analytics_summary: Mapped[Optional[dict]] = mapped_column(JSONB) # {attempt_count, correct_count, total_time_seconds, discrimination_index, calibrated_difficulty}

    # Relationships
    subject = relationship("Subject", lazy="selectin")
    chapter = relationship("Chapter", lazy="selectin")
    topic = relationship("Topic", lazy="selectin")
    subtopic = relationship("Subtopic", lazy="selectin")
    learning_objective = relationship("LearningObjective", lazy="selectin")
    author = relationship("User", lazy="selectin")
    
    options: Mapped[List["QuestionOption"]] = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", lazy="selectin")
    revisions: Mapped[List["QuestionRevision"]] = relationship("QuestionRevision", back_populates="question", cascade="all, delete-orphan", lazy="selectin")
    audit_logs: Mapped[List["QuestionAuditLog"]] = relationship("QuestionAuditLog", back_populates="question", cascade="all, delete-orphan", lazy="selectin")
    reports: Mapped[List["QuestionReport"]] = relationship("QuestionReport", back_populates="question", cascade="all, delete-orphan", lazy="selectin")
    
    mock_test_questions: Mapped[List["MockTestQuestion"]] = relationship("MockTestQuestion", back_populates="question", cascade="all, delete-orphan", lazy="selectin")
    previous_year_paper_questions: Mapped[List["PreviousYearPaperQuestion"]] = relationship("PreviousYearPaperQuestion", back_populates="question", cascade="all, delete-orphan", lazy="selectin")


class QuestionOption(BaseEntity):
    __tablename__ = "question_options"
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text)
    option_index: Mapped[int] = mapped_column(Integer, default=1)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    
    question: Mapped["Question"] = relationship("Question", back_populates="options", lazy="selectin")


class QuestionRelation(BaseEntity):
    __tablename__ = "question_relations"
    source_question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    target_question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    relation_type: Mapped[str] = mapped_column(String(50), default="RELATED") # PREREQUISITE, RELATED, SIMILAR


class QuestionRevision(BaseEntity):
    __tablename__ = "question_revisions"
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    snapshot: Mapped[dict] = mapped_column(JSONB)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    change_summary: Mapped[Optional[str]] = mapped_column(String(500))
    
    question: Mapped["Question"] = relationship("Question", back_populates="revisions")


class QuestionAuditLog(BaseEntity):
    __tablename__ = "question_audit_logs"
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(100))
    old_status: Mapped[Optional[str]] = mapped_column(String(50))
    new_status: Mapped[Optional[str]] = mapped_column(String(50))
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[Optional[str]] = mapped_column(String(500))
    
    question: Mapped["Question"] = relationship("Question", back_populates="audit_logs")


class QuestionReport(BaseEntity):
    __tablename__ = "question_reports"
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    reporter_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    report_type: Mapped[str] = mapped_column(String(50)) # WRONG_ANSWER, TYPO, UNCLEAR_EXPLANATION, OTHER
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="OPEN") # OPEN, UNDER_REVIEW, RESOLVED, REJECTED
    
    question: Mapped["Question"] = relationship("Question", back_populates="reports")


# --- Assessment Engine Structural Entities ---

class MockTest(BaseEntity):
    __tablename__ = "mock_tests"
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    total_marks: Mapped[float] = mapped_column(Float, default=0.0)
    
    questions: Mapped[List["MockTestQuestion"]] = relationship("MockTestQuestion", back_populates="mock_test", cascade="all, delete-orphan", lazy="selectin")


class MockTestQuestion(BaseEntity):
    __tablename__ = "mock_test_questions"
    mock_test_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mock_tests.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)
    marks: Mapped[float] = mapped_column(Float, default=1.0)
    negative_marks: Mapped[float] = mapped_column(Float, default=0.0)
    
    mock_test: Mapped["MockTest"] = relationship("MockTest", back_populates="questions", lazy="selectin")
    question: Mapped["Question"] = relationship("Question", back_populates="mock_test_questions", lazy="selectin")


class PreviousYearPaper(BaseEntity):
    __tablename__ = "previous_year_papers"
    exam_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_versions.id", ondelete="CASCADE"), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(255))
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    questions: Mapped[List["PreviousYearPaperQuestion"]] = relationship("PreviousYearPaperQuestion", back_populates="previous_year_paper", cascade="all, delete-orphan", lazy="selectin")


class PreviousYearPaperQuestion(BaseEntity):
    __tablename__ = "previous_year_paper_questions"
    paper_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("previous_year_papers.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)
    marks: Mapped[float] = mapped_column(Float, default=1.0)
    
    previous_year_paper: Mapped["PreviousYearPaper"] = relationship("PreviousYearPaper", back_populates="questions", lazy="selectin")
    question: Mapped["Question"] = relationship("Question", back_populates="previous_year_paper_questions", lazy="selectin")
