import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import BaseEntity

class ExamCategory(BaseEntity):
    __tablename__ = "exam_categories"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    
    exams: Mapped[List["Exam"]] = relationship("Exam", back_populates="category", cascade="all, delete-orphan", lazy="selectin")

class Exam(BaseEntity):
    __tablename__ = "exams"
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_categories.id", ondelete="RESTRICT"), index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    category: Mapped["ExamCategory"] = relationship("ExamCategory", back_populates="exams", lazy="selectin")
    versions: Mapped[List["ExamVersion"]] = relationship("ExamVersion", back_populates="exam", cascade="all, delete-orphan", lazy="selectin")
    current_affairs: Mapped[List["ExamCurrentAffair"]] = relationship("ExamCurrentAffair", back_populates="exam", cascade="all, delete-orphan", lazy="selectin")

class ExamVersion(BaseEntity):
    __tablename__ = "exam_versions"
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    cycle_name: Mapped[str] = mapped_column(String(100), index=True)  # e.g., "2025 Cycle"
    status: Mapped[str] = mapped_column(String(50), default="UPCOMING", index=True)
    notification_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    exam: Mapped["Exam"] = relationship("Exam", back_populates="versions", lazy="selectin")
    subjects: Mapped[List["ExamSubject"]] = relationship("ExamSubject", back_populates="exam_version", cascade="all, delete-orphan", lazy="selectin")
    selection_stages: Mapped[List["SelectionStage"]] = relationship("SelectionStage", back_populates="exam_version", cascade="all, delete-orphan", lazy="selectin")
    eligibility: Mapped[Optional["Eligibility"]] = relationship("Eligibility", back_populates="exam_version", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    languages: Mapped[List["ExamLanguage"]] = relationship("ExamLanguage", back_populates="exam_version", cascade="all, delete-orphan", lazy="selectin")

class Eligibility(BaseEntity):
    __tablename__ = "eligibilities"
    exam_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_versions.id", ondelete="CASCADE"), unique=True, index=True)
    age_min: Mapped[Optional[int]] = mapped_column(Integer)
    age_max: Mapped[Optional[int]] = mapped_column(Integer)
    education_req: Mapped[Optional[str]] = mapped_column(String(1000))
    additional_reqs: Mapped[Optional[str]] = mapped_column(String(1000))
    
    exam_version: Mapped["ExamVersion"] = relationship("ExamVersion", back_populates="eligibility", lazy="selectin")

class ExamLanguage(BaseEntity):
    __tablename__ = "exam_languages"
    exam_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_versions.id", ondelete="CASCADE"), index=True)
    language: Mapped[str] = mapped_column(String(50))
    
    exam_version: Mapped["ExamVersion"] = relationship("ExamVersion", back_populates="languages", lazy="selectin")

class SelectionStage(BaseEntity):
    __tablename__ = "selection_stages"
    exam_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_versions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100)) # e.g. Prelims, PET, Mains
    stage_order: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    exam_version: Mapped["ExamVersion"] = relationship("ExamVersion", back_populates="selection_stages", lazy="selectin")
    exam_pattern: Mapped[Optional["ExamPattern"]] = relationship("ExamPattern", back_populates="selection_stage", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    physical_requirements: Mapped[List["PhysicalRequirement"]] = relationship("PhysicalRequirement", back_populates="selection_stage", cascade="all, delete-orphan", lazy="selectin")

class ExamPattern(BaseEntity):
    __tablename__ = "exam_patterns"
    selection_stage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("selection_stages.id", ondelete="CASCADE"), unique=True, index=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    total_marks: Mapped[Optional[float]] = mapped_column()
    total_questions: Mapped[Optional[int]] = mapped_column(Integer)
    negative_marking_ratio: Mapped[Optional[float]] = mapped_column() # e.g. 0.25
    
    selection_stage: Mapped["SelectionStage"] = relationship("SelectionStage", back_populates="exam_pattern", lazy="selectin")

class PhysicalRequirement(BaseEntity):
    __tablename__ = "physical_requirements"
    selection_stage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("selection_stages.id", ondelete="CASCADE"), index=True)
    gender: Mapped[str] = mapped_column(String(20)) # MALE, FEMALE
    category: Mapped[Optional[str]] = mapped_column(String(50)) # e.g. General, SC/ST for relaxations
    height_cm: Mapped[Optional[float]] = mapped_column()
    chest_normal_cm: Mapped[Optional[float]] = mapped_column()
    chest_expanded_cm: Mapped[Optional[float]] = mapped_column()
    running_event: Mapped[Optional[str]] = mapped_column(String(200)) # e.g. 1600m in 7 mins
    long_jump: Mapped[Optional[str]] = mapped_column(String(100))
    shot_put: Mapped[Optional[str]] = mapped_column(String(100))
    
    selection_stage: Mapped["SelectionStage"] = relationship("SelectionStage", back_populates="physical_requirements", lazy="selectin")

class Subject(BaseEntity):
    __tablename__ = "subjects"
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    exam_versions: Mapped[List["ExamSubject"]] = relationship("ExamSubject", back_populates="subject", cascade="all, delete-orphan", lazy="selectin")
    chapters: Mapped[List["Chapter"]] = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan", lazy="selectin")

class ExamSubject(BaseEntity):
    __tablename__ = "exam_subjects"
    exam_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_versions.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    weightage: Mapped[int] = mapped_column(Integer, default=1)
    
    exam_version: Mapped["ExamVersion"] = relationship("ExamVersion", back_populates="subjects", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="exam_versions", lazy="selectin")

class Chapter(BaseEntity):
    __tablename__ = "chapters"
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    subject: Mapped["Subject"] = relationship("Subject", back_populates="chapters", lazy="selectin")
    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="chapter", cascade="all, delete-orphan", lazy="selectin")

class Topic(BaseEntity):
    __tablename__ = "topics"
    chapter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="topics", lazy="selectin")
