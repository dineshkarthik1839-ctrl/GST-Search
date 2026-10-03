import hashlib
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=getattr(settings, "access_token_expire_minutes", 60)
        )
    
    iat = datetime.now(timezone.utc)
    to_encode = {
        "exp": expire,
        "iat": iat,
        "sub": str(subject),
        "iss": getattr(settings, "project_name", "COMPANYLENS"),
        "aud": "companylens_api",
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any], 
    jti: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=getattr(settings, "refresh_token_expire_days", 7)
        )
    
    iat = datetime.now(timezone.utc)
    to_encode = {
        "exp": expire,
        "iat": iat,
        "sub": str(subject),
        "iss": getattr(settings, "project_name", "COMPANYLENS"),
        "aud": "companylens_api",
        "jti": jti
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[ALGORITHM],
            audience="companylens_api",
            issuer=getattr(settings, "project_name", "COMPANYLENS")
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError:
        raise ValueError("Could not validate token")

def hash_identifier(value: str) -> str:
    """
    Cryptographic SHA-256 hash of normalized identifier for secure internal matching.
    Never stores or searches raw PAN unnecessarily.
    """
    if not value:
        return ""
    normalized = value.strip().upper()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def mask_pan(pan: Optional[str]) -> str:
    """
    Safely masks a PAN for display: ABCDE****F
    Never exposes full PAN in open contexts without explicit permission.
    """
    if not pan or len(pan) < 10:
        return ""
    return f"{pan[:5]}****{pan[-1]}"

def sanitize_log_message(msg: str) -> str:
    """
    Sanitizes log messages to ensure PAN, tokens, passwords, and secret keys
    are never leaked into console or file logs.
    """
    if not msg:
        return ""
    # Redact PAN pattern [A-Z]{5}[0-9]{4}[A-Z]{1}
    msg = re.sub(r'\b([A-Z]{5})[0-9]{4}([A-Z]{1})\b', r'\1****\2', msg)
    # Redact common secret patterns
    msg = re.sub(r'(api_key|client_secret|password|secret|token)=([^\s&]+)', r'\1=***REDACTED***', msg, flags=re.IGNORECASE)
    return msg

