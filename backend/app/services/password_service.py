# Password Service - Business logic for password operations
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.repositories import UserRepository, PasswordResetRepository
from app.api.deps import (
    hash_password,
    verify_password,
    create_password_reset_token,
    decode_password_reset_token,
    update_user_password_and_revoke_sessions,
)
from app.models.password_reset import PasswordResetToken


class PasswordService:
    """Service layer for password operations"""
    
    @staticmethod
    def request_password_reset(db: Session, email: str) -> tuple[PasswordResetToken, str]:
        """
        Request password reset - create token
        
        Returns:
            (password_reset_token_record, jwt_token_plaintext)
        """
        from app.api.deps import PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        
        user = UserRepository.get_by_email(db, email)
        
        # Always return generic message (security: don't reveal if email exists)
        if not user:
            return None, None
        
        # Create JWT token
        jwt_token = create_password_reset_token(user.id)
        
        # Hash JWT for deterministic lookup
        import hmac
        import hashlib
        from app.api.deps import REFRESH_TOKEN_PEPPER
        
        token_hash = hmac.new(
            REFRESH_TOKEN_PEPPER.encode("utf-8"),
            jwt_token.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        # Calculate expiry
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        
        # Create token record in DB
        token_record = PasswordResetRepository.create(
            db,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        db.commit()
        
        return token_record, jwt_token
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> None:
        """
        Reset password using token
        """
        # Decode JWT token
        try:
            payload = decode_password_reset_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        user_id_str = payload.get("sub")
        user_id = uuid.UUID(user_id_str)
        
        # Get user
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        # Get password reset token record
        import hmac
        import hashlib
        from app.api.deps import REFRESH_TOKEN_PEPPER
        
        token_hash = hmac.new(
            REFRESH_TOKEN_PEPPER.encode("utf-8"),
            token.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        reset_token = PasswordResetRepository.get_valid_by_hash(db, token_hash)
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        # Update password and revoke sessions
        update_user_password_and_revoke_sessions(user, new_password, db)
        
        # Mark token as used
        PasswordResetRepository.mark_used(db, reset_token)
        
        db.commit()
    
    @staticmethod
    def change_password(db: Session, user, current_password: str, new_password: str) -> None:
        """
        Change password when user is authenticated
        """
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid current password"
            )
        
        # Check new password is different
        if verify_password(new_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password same as current"
            )
        
        # Update password and revoke sessions
        update_user_password_and_revoke_sessions(user, new_password, db)
        
        db.commit()
