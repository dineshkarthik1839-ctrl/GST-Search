import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import BaseEntity
import enum

class TokenType(str, enum.Enum):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"

class LoginStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class UserSession(BaseEntity):
    __tablename__ = "user_sessions"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    refresh_token_jti: Mapped[str] = mapped_column(String(255), unique=True, index=True) # Storing JTI for fast lookup or full hash
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    device_info: Mapped[Optional[str]] = mapped_column(Text)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

class LoginHistory(BaseEntity):
    __tablename__ = "login_history"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    device_info: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[LoginStatus] = mapped_column(Enum(LoginStatus), index=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255))

class VerificationToken(BaseEntity):
    __tablename__ = "verification_tokens"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    token_type: Mapped[TokenType] = mapped_column(Enum(TokenType))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
