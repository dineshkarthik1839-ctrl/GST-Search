import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import BaseEntity
import enum

class BookmarkType(str, enum.Enum):
    QUESTION = "QUESTION"
    RESOURCE = "RESOURCE"

class Bookmark(BaseEntity):
    __tablename__ = "bookmarks"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    entity_type: Mapped[BookmarkType] = mapped_column(Enum(BookmarkType))
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True)

class UserProgress(BaseEntity):
    __tablename__ = "user_progress"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    completion_percentage: Mapped[Float] = mapped_column(Float, default=0.0)

class StudyPlan(BaseEntity):
    __tablename__ = "study_plans"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    
    sessions: Mapped[List["StudySession"]] = relationship("StudySession", back_populates="study_plan", cascade="all, delete-orphan", lazy="selectin")

class StudySession(BaseEntity):
    __tablename__ = "study_sessions"
    study_plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("study_plans.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_completed: Mapped[bool] = mapped_column(default=False)
    
    study_plan: Mapped["StudyPlan"] = relationship("StudyPlan", back_populates="sessions", lazy="selectin")

class Notification(BaseEntity):
    __tablename__ = "notifications"
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[Text] = mapped_column(Text)
    
    user_notifications: Mapped[List["UserNotification"]] = relationship("UserNotification", back_populates="notification", cascade="all, delete-orphan", lazy="selectin")

class UserNotification(BaseEntity):
    __tablename__ = "user_notifications"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    notification_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), index=True)
    is_read: Mapped[bool] = mapped_column(default=False)
    
    notification: Mapped["Notification"] = relationship("Notification", back_populates="user_notifications", lazy="selectin")

class Discussion(BaseEntity):
    __tablename__ = "discussions"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Text] = mapped_column(Text)
    
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="discussion", cascade="all, delete-orphan", lazy="selectin")

class Comment(BaseEntity):
    __tablename__ = "comments"
    discussion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("discussions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content: Mapped[Text] = mapped_column(Text)
    
    discussion: Mapped["Discussion"] = relationship("Discussion", back_populates="comments", lazy="selectin")

class PhysicalActivity(BaseEntity):
    __tablename__ = "physical_activities"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    activity_type: Mapped[str] = mapped_column(String(100))
    value: Mapped[Float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(50))
