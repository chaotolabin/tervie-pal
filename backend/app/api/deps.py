# Authentication & dependency utilities
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt
import os
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.auth import User, RefreshSession


# ==================== Configuration ====================
# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ==================== Password Management ====================
def hash_password(password: str) -> str:
    """Hash password using argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


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
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token() -> tuple[str, str]:
    """
    Create JWT refresh token
    
    Returns:
        (token, token_hash) - raw token and its hash for storage
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4())  # unique identifier
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    token_hash = hash_password(token)  # store hash for security
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ==================== User Dependencies ====================
async def get_current_user(
    token: str = None,
    db: Session = Depends(get_db)
) -> User:
    """
    Extract current user from JWT access token in Authorization header
    
    Usage:
        @app.get("/users/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
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
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized (admin only)"
        )
    
    return current_user