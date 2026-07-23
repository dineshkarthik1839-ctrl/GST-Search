from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.rate_limit import RateLimiter
from app.modules.users.models import User
from app.modules.auth.schemas import (
    TokenResponse, LoginRequest, RefreshTokenRequest, SessionResponse, MessageResponse
)
from app.modules.auth.service import (
    authenticate_user, create_session_for_user, refresh_session, 
    revoke_session, revoke_all_sessions, get_active_sessions, hash_token
)
from app.core.security import decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def set_auth_cookies(response: Response, tokens: dict):
    if settings.use_httponly_cookies:
        response.set_cookie(
            key="access_token", 
            value=tokens["access_token"], 
            httponly=True, 
            secure=settings.cookie_secure, 
            samesite="lax",
            max_age=tokens["expires_in"]
        )
        response.set_cookie(
            key="refresh_token", 
            value=tokens["refresh_token"], 
            httponly=True, 
            secure=settings.cookie_secure, 
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 86400
        )

def clear_auth_cookies(response: Response):
    if settings.use_httponly_cookies:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else "127.0.0.1"
    device_info = request.headers.get("user-agent", "Unknown")
    
    # form_data.username will contain the email
    user = authenticate_user(db, form_data.username, form_data.password, ip_address, device_info)
    tokens = create_session_for_user(db, user.id, ip_address, device_info)
    
    set_auth_cookies(response, tokens)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, refresh_data: RefreshTokenRequest = None, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else "127.0.0.1"
    device_info = request.headers.get("user-agent", "Unknown")
    
    token = None
    if refresh_data and refresh_data.refresh_token:
        token = refresh_data.refresh_token
    elif settings.use_httponly_cookies and "refresh_token" in request.cookies:
        token = request.cookies.get("refresh_token")
        
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    tokens = refresh_session(db, token, ip_address, device_info)
    set_auth_cookies(response, tokens)
    return tokens

@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # To logout, we need to know the current refresh token or access token to invalidate the session.
    # We can get the refresh token from cookie or body, or we can just get JTI from access token and find the session.
    # Actually, access token doesn't map 1:1 to session in DB since session tracks refresh token.
    # The best way is to extract refresh token and revoke it.
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                hashed_jti = hash_token(jti)
                from app.modules.auth.repository import UserSessionRepository
                repo = UserSessionRepository(db)
                session = repo.get_by_field("refresh_token_jti", hashed_jti)
                if session and session.user_id == current_user.id:
                    session.is_revoked = True
                    db.commit()
        except Exception:
            pass # Ignore token decode errors on logout
            
    clear_auth_cookies(response)
    return {"message": "Successfully logged out"}

@router.post("/logout-all", response_model=MessageResponse)
def logout_all(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    revoke_all_sessions(db, current_user.id)
    clear_auth_cookies(response)
    return {"message": "Successfully logged out of all devices"}

@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = get_active_sessions(db, current_user.id)
    
    current_jti_hash = None
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            if payload.get("jti"):
                current_jti_hash = hash_token(payload.get("jti"))
        except Exception:
            pass
            
    result = []
    for s in sessions:
        result.append(SessionResponse(
            id=s.id,
            ip_address=s.ip_address,
            device_info=s.device_info,
            created_at=s.created_at,
            expires_at=s.expires_at,
            is_current=(s.refresh_token_jti == current_jti_hash)
        ))
    return result

@router.post("/forgot-password", response_model=MessageResponse, dependencies=[Depends(RateLimiter(times=3, seconds=3600))])
def forgot_password(request: Request, db: Session = Depends(get_db)):
    # Placeholder for email sending logic
    return {"message": "If that email exists, a reset link has been sent."}

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: Request, db: Session = Depends(get_db)):
    # Placeholder for token validation and password reset logic
    return {"message": "Password successfully reset."}

@router.post("/verify-email", response_model=MessageResponse)
def verify_email(request: Request, db: Session = Depends(get_db)):
    # Placeholder for email verification
    return {"message": "Email successfully verified."}
