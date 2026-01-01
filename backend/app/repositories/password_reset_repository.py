# Password Reset Token Repository
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.password_reset import PasswordResetToken
import uuid


class PasswordResetRepository:
    """Repository for PasswordResetToken operations"""
    
    @staticmethod
    def create(db: Session, user_id: uuid.UUID, token_hash: str, expires_at) -> PasswordResetToken:
        """Create new password reset token"""
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.add(token)
        return token
    
    @staticmethod
    def get_by_token_hash(db: Session, token_hash: str) -> PasswordResetToken | None:
        """Get token by hash"""
        return db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        ).scalar_one_or_none()
    
    @staticmethod
    def mark_used(db: Session, token: PasswordResetToken) -> PasswordResetToken:
        """Mark token as used"""
        from datetime import datetime, timezone
        token.used_at = datetime.now(timezone.utc)
        return token
    
    @staticmethod
    def revoke(db: Session, token: PasswordResetToken) -> PasswordResetToken:
        """Revoke token"""
        from datetime import datetime, timezone
        token.revoked_at = datetime.now(timezone.utc)
        return token
    
    @staticmethod
    def get_valid_by_hash(db: Session, token_hash: str) -> PasswordResetToken | None:
        """Get valid (not expired, not used, not revoked) token by hash"""
        token = PasswordResetRepository.get_by_token_hash(db, token_hash)
        if token and token.is_valid():
            return token
        return None
