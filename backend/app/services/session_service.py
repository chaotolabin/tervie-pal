# Session Service - Business logic for refresh sessions
from sqlalchemy.orm import Session

from app.repositories import RefreshTokenRepository
from app.models.auth import RefreshSession


class SessionService:
    """Service layer for refresh session operations"""
    
    @staticmethod
    def get_user_sessions(db: Session, user_id) -> list[RefreshSession]:
        """Get all active refresh sessions for user"""
        return RefreshTokenRepository.get_active_for_user(db, user_id)
    
    @staticmethod
    def revoke_session(db: Session, session: RefreshSession) -> None:
        """Revoke a specific refresh session"""
        RefreshTokenRepository.revoke(db, session)
        db.commit()
    
    @staticmethod
    def revoke_all_sessions(db: Session, user_id) -> int:
        """Revoke all refresh sessions for user, return count revoked"""
        count = RefreshTokenRepository.revoke_all_for_user(db, user_id)
        db.commit()
        return count
