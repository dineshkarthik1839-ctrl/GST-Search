from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_token
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = decode_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        user_repo = UserRepository(db)
        return user_repo.get_by_id(uuid.UUID(user_id))
    except Exception:
        return None

class RequireRole:
    def __init__(self, role_name: str):
        self.role_name = role_name

    def __call__(self, current_user: User = Depends(get_current_user)):
        for role in current_user.roles:
            if role.name == self.role_name or role.name == "Super Admin":
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )

class RequirePermission:
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    def __call__(self, current_user: User = Depends(get_current_user)):
        for role in current_user.roles:
            if role.name == "Super Admin":
                return current_user
            for perm in role.permissions:
                if perm.name == self.permission_name:
                    return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
