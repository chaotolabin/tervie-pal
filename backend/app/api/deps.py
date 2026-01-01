# Authentication & dependency utilities
# Security functions: password hashing, token generation/verification
# Used by: routes (thin layer), services (business logic), repositories
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
import hmac
import hashlib

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from passlib.context import CryptContext

from app.core.database import get_db
from app.models.auth import User, RefreshSession


# ==================== Configuration ====================
# HTTPBearer for automatic Authorization: Bearer token extraction
security = HTTPBearer()

# Password hashing - Argon2 (OWASP recommended)
# Cấu hình an toàn tối đa:
# - time_cost=3: 3 iterations (đủ an toàn, ~0.5s)
# - memory_cost=65536: 64MB memory (kháng brute-force)
# - parallelism=4: 4 cores parallel
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=3,
    argon2__memory_cost=65536,
    argon2__parallelism=4
)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 0  # DEV MODE: 0 để test token hết hạn ngay
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15

# Pepper riêng cho refresh token hashing (khuyến nghị khác SECRET_KEY)
REFRESH_TOKEN_PEPPER = os.getenv("REFRESH_TOKEN_PEPPER", SECRET_KEY)


# ==================== Password Management ====================
def hash_password(password: str) -> str:
    """Hash password using argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ==================== Refresh Token Hashing (Deterministic & Secure) ====================
def hash_refresh_token(token: str) -> str:
    """
    Hash refresh token for storage (deterministic, lookup-friendly).
    Use HMAC-SHA256(pepper, token).
    """
    return hmac.new(
        REFRESH_TOKEN_PEPPER.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


# ==================== Token Management ====================
def create_access_token(user_id: uuid.UUID, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User UUID
        expires_delta: Token expiration time (default: 30 minutes)
    
    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, str]:
    """
    Create JWT refresh token
    
    Returns:
        (token, token_hash) - raw token and its hash for storage
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4()),  # unique identifier
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    token_hash = hash_refresh_token(token)
    return token, token_hash


def create_signup_token(session_id: uuid.UUID, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT signup token (short-lived, 24 hours)
    
    Args:
        session_id: Signup session UUID
        expires_delta: Token expiration time (default: 24 hours)
    
    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": str(session_id),
        "exp": expire,
        "type": "signup",
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_signup_token(token: str) -> dict:
    """
    Decode signup token
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "signup":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signup token"
            )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    token_hash = hash_refresh_token(token)  # store deterministic hash for lookup
    return token, token_hash


def decode_token(token: str) -> dict:
    """
    Decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def create_password_reset_token(user_id: uuid.UUID) -> str:
    """
    Create JWT password reset token (15 minutes expiry)
    
    Args:
        user_id: User UUID
    
    Returns:
        JWT token string
    """
    expires_delta = timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "password_reset",
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_password_reset_token(token: str) -> dict:
    """
    Decode password reset token
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload
    
    Raises:
        Exception: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            raise InvalidTokenError("Invalid token type")
        return payload
    except (ExpiredSignatureError, InvalidTokenError) as e:
        raise e


def update_user_password_and_revoke_sessions(
    user: User,
    new_password: str,
    db: Session
) -> None:
    """
    Utility: Update user password + revoke ALL refresh sessions
    
    Sử dụng cho:
    - Change password (verify current password trước)
    - Reset password (verify reset token trước)
    
    Args:
        user: User object
        new_password: Plain text password
        db: Database session
    """
    from sqlalchemy import update
    
    # Update password
    user.password_hash = hash_password(new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    db.add(user)
    
    # Revoke ALL refresh sessions (logout all devices)
    db.execute(
        update(RefreshSession)
        .where(RefreshSession.user_id == user.id)
        .values(revoked_at=datetime.now(timezone.utc))
    )


# ==================== User Dependencies ====================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract current user from JWT access token in Authorization header
    
    Usage:
        @app.get("/users/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Requires: Authorization: Bearer <token>
    
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    # HTTPBearer automatically extracts token from "Authorization: Bearer <token>"
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    # Query user from database
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure current user is admin
    
    Usage:
        @app.get("/admin/dashboard")
        async def admin_dashboard(admin: User = Depends(get_current_admin_user)):
            return admin
    
    Raises:
        HTTPException: If user is not admin
    """
    if str(current_user.role) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized (admin only)"
        )
    
    return current_user
