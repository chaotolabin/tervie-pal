# Auth Service - Business logic for authentication
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.repositories import UserRepository, RefreshTokenRepository
from app.api.deps import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    decode_token,
)
from app.models.auth import User


class AuthService:
    """Service layer for authentication operations"""
    
    @staticmethod
    def register(
        db: Session,
        username: str,
        email: str,
        password: str,
        **user_data
    ) -> tuple[User, str, str]:
        """
        Register new user and return user with tokens
        
        Returns:
            (user, access_token, refresh_token)
        """
        # Check if user already exists
        if UserRepository.get_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if UserRepository.get_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        user = UserRepository.create(
            db,
            username=username,
            email=email,
            password_hash=hash_password(password),
            **user_data
        )
        db.add(user)
        db.flush()  # Generate user.id
        
        # Create tokens
        access_token = create_access_token(user.id)
        refresh_token, refresh_token_hash = create_refresh_token(user.id)
        
        # Store refresh token
        RefreshTokenRepository.create(
            db,
            user_id=user.id,
            token_hash=refresh_token_hash
        )
        
        db.commit()
        db.refresh(user)
        
        return user, access_token, refresh_token
    
    @staticmethod
    def login(
        db: Session,
        email_or_username: str,
        password: str,
        device_label: str = None,
        user_agent: str = None,
        ip: str = None
    ) -> tuple[User, str, str]:
        """
        Login user and return user with tokens
        
        Returns:
            (user, access_token, refresh_token)
        """
        # Find user
        user = UserRepository.get_by_email_or_username(db, email_or_username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password"
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password"
            )
        
        # Create tokens
        access_token = create_access_token(user.id)
        refresh_token, refresh_token_hash = create_refresh_token(user.id)
        
        # Store refresh token
        RefreshTokenRepository.create(
            db,
            user_id=user.id,
            token_hash=refresh_token_hash,
            device_label=device_label,
            user_agent=user_agent,
            ip=ip
        )
        
        db.commit()
        
        return user, access_token, refresh_token
    
    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str
    ) -> tuple[str, str]:
        """
        Refresh access token using refresh token
        
        Returns:
            (new_access_token, new_refresh_token)
        """
        # Decode refresh token
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user_id_str = payload.get("sub")
        user_id = uuid.UUID(user_id_str)
        
        # Verify refresh token is stored and not revoked
        refresh_token_hash = hash_refresh_token(refresh_token)
        session = RefreshTokenRepository.get_by_token_hash(db, refresh_token_hash)
        
        if not session or session.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalid or revoked"
            )
        
        # Update last used
        RefreshTokenRepository.update_last_used(db, session)
        
        # Create new tokens
        new_access_token = create_access_token(user_id)
        new_refresh_token, new_refresh_token_hash = create_refresh_token(user_id)
        
        # Replace old refresh token with new one
        RefreshTokenRepository.revoke(db, session)
        RefreshTokenRepository.create(
            db,
            user_id=user_id,
            token_hash=new_refresh_token_hash
        )
        
        db.commit()
        
        return new_access_token, new_refresh_token
    
    @staticmethod
    def logout(db: Session, refresh_token: str) -> None:
        """Logout user - revoke refresh token"""
        refresh_token_hash = hash_refresh_token(refresh_token)
        session = RefreshTokenRepository.get_by_token_hash(db, refresh_token_hash)
        
        if session:
            RefreshTokenRepository.revoke(db, session)
            db.commit()
