import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.auth.models import UserSession, LoginHistory, LoginStatus
from app.modules.auth.repository import UserSessionRepository, LoginHistoryRepository

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def record_login_attempt(db: Session, user: User, ip_address: str, device_info: str, success: bool, reason: str = ""):
    history_repo = LoginHistoryRepository(db)
    history_repo.create({
        "user_id": user.id,
        "ip_address": ip_address,
        "device_info": device_info,
        "status": LoginStatus.SUCCESS if success else LoginStatus.FAILED,
        "reason": reason
    })
    
    if success:
        user.failed_login_attempts = 0
        user.locked_until = None
    else:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
    db.commit()

def authenticate_user(db: Session, email: str, password: str, ip_address: str, device_info: str) -> User:
    user_repo = UserRepository(db)
    user = user_repo.get_by_field("email", email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
        
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is temporarily locked due to multiple failed login attempts")

    if not user.password_hash or not verify_password(password, user.password_hash):
        record_login_attempt(db, user, ip_address, device_info, False, "Invalid password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
    record_login_attempt(db, user, ip_address, device_info, True, "Logged in")
    return user

def create_session_for_user(db: Session, user_id: uuid.UUID, ip_address: str, device_info: str):
    access_token = create_access_token(subject=user_id)
    jti = str(uuid.uuid4())
    refresh_token = create_refresh_token(subject=user_id, jti=jti)
    
    session_repo = UserSessionRepository(db)
    session_repo.create({
        "user_id": user_id,
        "refresh_token_jti": hash_token(jti),
        "ip_address": ip_address,
        "device_info": device_info,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": settings.access_token_expire_minutes * 60,
        "token_type": "bearer"
    }

def refresh_session(db: Session, refresh_token: str, ip_address: str, device_info: str):
    try:
        payload = decode_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        
    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token structure")
        
    session_repo = UserSessionRepository(db)
    hashed_jti = hash_token(jti)
    session = session_repo.get_by_field("refresh_token_jti", hashed_jti)
    
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")
        
    if session.is_revoked:
        # Token reuse detected! Revoke all sessions for this user.
        db.execute(
            session_repo.model.__table__.update()
            .where(session_repo.model.user_id == uuid.UUID(user_id))
            .values(is_revoked=True)
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token reuse detected. All sessions revoked.")
        
    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        
    # Rotate token: revoke old one, create new one
    session.is_revoked = True
    db.commit()
    
    return create_session_for_user(db, uuid.UUID(user_id), ip_address, device_info)

def get_active_sessions(db: Session, user_id: uuid.UUID):
    session_repo = UserSessionRepository(db)
    return db.execute(
        session_repo.model.__table__.select().where(
            session_repo.model.user_id == user_id,
            session_repo.model.is_revoked == False,
            session_repo.model.expires_at > datetime.now(timezone.utc)
        )
    ).mappings().all()

def revoke_session(db: Session, user_id: uuid.UUID, session_id: uuid.UUID):
    session_repo = UserSessionRepository(db)
    session = session_repo.get_by_id(session_id)
    if session and session.user_id == user_id:
        session.is_revoked = True
        db.commit()

def revoke_all_sessions(db: Session, user_id: uuid.UUID):
    session_repo = UserSessionRepository(db)
    db.execute(
        session_repo.model.__table__.update()
        .where(session_repo.model.user_id == user_id)
        .values(is_revoked=True)
    )
    db.commit()

