import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import BaseEntity
import enum

class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    SUBJECTIVE = "SUBJECTIVE"
    TRUE_FALSE = "TRUE_FALSE"

class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Question(BaseEntity):
    __tablename__ = "questions"
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), index=True)
    content: Mapped[str] = mapped_column(Text)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), default=QuestionType.MCQ)
    difficulty: Mapped[DifficultyLevel] = mapped_column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    
    options: Mapped[List["QuestionOption"]] = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", lazy="selectin")
    mock_test_questions: Mapped[List["MockTestQuestion"]] = relationship("MockTestQuestion", back_populates="question", cascade="all, delete-orphan", lazy="selectin")
    previous_year_paper_questions: Mapped[List["PreviousYearPaperQuestion"]] = relationship("PreviousYearPaperQuestion", back_populates="question", cascade="all, delete-orphan", lazy="selectin")

class QuestionOption(BaseEntity):
    __tablename__ = "question_options"
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(String(500))
    is_correct: Mapped[bool] = mapped_column(default=False)
    
    question: Mapped["Question"] = relationship("Question", back_populates="options", lazy="selectin")

class MockTest(BaseEntity):
    __tablename__ = "mock_tests"
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    total_marks: Mapped[Float] = mapped_column(Float, default=0.0)
    
    questions: Mapped[List["MockTestQuestion"]] = relationship("MockTestQuestion", back_populates="mock_test", cascade="all, delete-orphan", lazy="selectin")

class MockTestQuestion(BaseEntity):
    __tablename__ = "mock_test_questions"
    mock_test_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mock_tests.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)
    marks: Mapped[Float] = mapped_column(Float, default=1.0)
    negative_marks: Mapped[Float] = mapped_column(Float, default=0.0)
    
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
    marks: Mapped[Float] = mapped_column(Float, default=1.0)
    
    previous_year_paper: Mapped["PreviousYearPaper"] = relationship("PreviousYearPaper", back_populates="questions", lazy="selectin")
    question: Mapped["Question"] = relationship("Question", back_populates="previous_year_paper_questions", lazy="selectin")
