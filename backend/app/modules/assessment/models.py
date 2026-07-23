import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Enum, Text, Float, Boolean, Table, Column, func
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


# --- Epic 1 Platform Learning & Attempt Entities ---

class LearningMode(str, enum.Enum):
    LEARNING = "LEARNING"
    PRACTICE = "PRACTICE"
    TIMED_PRACTICE = "TIMED_PRACTICE"
    EXAM_SIMULATION = "EXAM_SIMULATION"
    REVISION = "REVISION"
    WEAK_TOPIC_PRACTICE = "WEAK_TOPIC_PRACTICE"
    BOOKMARKED_QUESTIONS = "BOOKMARKED_QUESTIONS"
    PREVIOUS_YEAR_PRACTICE = "PREVIOUS_YEAR_PRACTICE"
    DAILY_CHALLENGE = "DAILY_CHALLENGE"
    MARATHON = "MARATHON"


class QuestionMasteryStatus(str, enum.Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    CORRECT_ONCE = "CORRECT_ONCE"
    CORRECT_MULTIPLE = "CORRECT_MULTIPLE"
    INCORRECT = "INCORRECT"
    NEEDS_REVISION = "NEEDS_REVISION"
    MASTERED = "MASTERED"
    BOOKMARKED = "BOOKMARKED"


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    PAUSED = "PAUSED"


class AttemptQuestionStatus(str, enum.Enum):
    UNVISITED = "UNVISITED"
    VISITED = "VISITED"
    ANSWERED = "ANSWERED"
    MARKED_FOR_REVIEW = "MARKED_FOR_REVIEW"
    ANSWERED_AND_MARKED = "ANSWERED_AND_MARKED"


class Attempt(BaseEntity):
    __tablename__ = "attempts"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    mock_test_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mock_tests.id", ondelete="SET NULL"), index=True)
    practice_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("practice_sessions.id", ondelete="SET NULL"), index=True)
    
    mode: Mapped[LearningMode] = mapped_column(Enum(LearningMode), default=LearningMode.EXAM_SIMULATION, index=True)
    status: Mapped[AttemptStatus] = mapped_column(Enum(AttemptStatus), default=AttemptStatus.IN_PROGRESS, index=True)
    
    start_time: Mapped[datetime] = mapped_column(default=func.now())
    end_time: Mapped[Optional[datetime]] = mapped_column()
    time_taken_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    score: Mapped[float] = mapped_column(Float, default=0.0)
    total_marks: Mapped[float] = mapped_column(Float, default=0.0)
    accuracy_pct: Mapped[float] = mapped_column(Float, default=0.0)
    speed_seconds_per_q: Mapped[float] = mapped_column(Float, default=0.0)
    
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Offline sync readiness & AI-ready metadata
    client_sync_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    ai_learning_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    attempt_questions: Mapped[List["AttemptQuestion"]] = relationship("AttemptQuestion", back_populates="attempt", cascade="all, delete-orphan", lazy="selectin")
    exam_result: Mapped[Optional["ExamResult"]] = relationship("ExamResult", back_populates="attempt", uselist=False, lazy="selectin")
    mock_test = relationship("MockTest", lazy="selectin")


class AttemptQuestion(BaseEntity):
    __tablename__ = "attempt_questions"
    
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)
    selected_option_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("question_options.id", ondelete="SET NULL"))
    user_answer_text: Mapped[Optional[str]] = mapped_column(Text)
    
    status: Mapped[AttemptQuestionStatus] = mapped_column(Enum(AttemptQuestionStatus), default=AttemptQuestionStatus.UNVISITED, index=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    marks_obtained: Mapped[float] = mapped_column(Float, default=0.0)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    attempt: Mapped["Attempt"] = relationship("Attempt", back_populates="attempt_questions", lazy="selectin")
    question: Mapped["Question"] = relationship("Question", lazy="selectin")


class PracticeSession(BaseEntity):
    __tablename__ = "practice_sessions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subjects.id", ondelete="SET NULL"), index=True)
    topic_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), index=True)
    
    mode: Mapped[LearningMode] = mapped_column(Enum(LearningMode), default=LearningMode.PRACTICE, index=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=10)
    status: Mapped[AttemptStatus] = mapped_column(Enum(AttemptStatus), default=AttemptStatus.IN_PROGRESS, index=True)


class ExamResult(BaseEntity):
    __tablename__ = "exam_results"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exam_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("exams.id", ondelete="SET NULL"), index=True)
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"), unique=True, index=True)
    
    score: Mapped[float] = mapped_column(Float, default=0.0)
    percentile: Mapped[float] = mapped_column(Float, default=0.0)
    rank: Mapped[int] = mapped_column(Integer, default=0)
    
    strengths_json: Mapped[Optional[dict]] = mapped_column(JSONB) # list of strong topics
    weaknesses_json: Mapped[Optional[dict]] = mapped_column(JSONB) # list of weak topics
    recommendations_json: Mapped[Optional[dict]] = mapped_column(JSONB) # AI recommended study items
    
    attempt: Mapped["Attempt"] = relationship("Attempt", back_populates="exam_result", lazy="selectin")


class Leaderboard(BaseEntity):
    __tablename__ = "leaderboard"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exam_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    mock_test_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mock_tests.id", ondelete="SET NULL"), index=True)
    
    score: Mapped[float] = mapped_column(Float, default=0.0)
    rank: Mapped[int] = mapped_column(Integer, default=1)
    percentile: Mapped[float] = mapped_column(Float, default=100.0)
    period: Mapped[str] = mapped_column(String(50), default="ALL_TIME", index=True) # WEEKLY, MONTHLY, ALL_TIME
    
    user = relationship("User", lazy="selectin")


class DailyActivity(BaseEntity):
    __tablename__ = "daily_activity"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    activity_date: Mapped[str] = mapped_column(String(20), index=True) # YYYY-MM-DD
    study_time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    questions_solved: Mapped[int] = mapped_column(Integer, default=0)
    tests_taken: Mapped[int] = mapped_column(Integer, default=0)


class RevisionQueue(BaseEntity):
    __tablename__ = "revision_queue"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    
    scheduled_for: Mapped[datetime] = mapped_column(index=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    interval_days: Mapped[int] = mapped_column(Integer, default=1)
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5) # SuperMemo SM-2 factor
    
    question = relationship("Question", lazy="selectin")


class QuestionMastery(BaseEntity):
    __tablename__ = "question_mastery"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    
    status: Mapped[QuestionMasteryStatus] = mapped_column(Enum(QuestionMasteryStatus), default=QuestionMasteryStatus.NOT_ATTEMPTED, index=True)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    times_incorrect: Mapped[int] = mapped_column(Integer, default=0)
    last_attempted_at: Mapped[Optional[datetime]] = mapped_column()


class StudyStatistics(BaseEntity):
    __tablename__ = "study_statistics"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    total_questions_attempted: Mapped[int] = mapped_column(Integer, default=0)
    overall_accuracy_pct: Mapped[float] = mapped_column(Float, default=0.0)
    current_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    learning_health_score: Mapped[float] = mapped_column(Float, default=100.0) # 0-100 score
    retention_pct: Mapped[float] = mapped_column(Float, default=85.0)
    
    subject_accuracy_json: Mapped[Optional[dict]] = mapped_column(JSONB)

