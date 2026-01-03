# Refresh Token Repository
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.auth import RefreshSession
import uuid


class RefreshTokenRepository:
    """Repository for RefreshSession operations"""
    
    @staticmethod
    def create(db: Session, user_id: uuid.UUID, token_hash: str, device_label: str = None, 
               user_agent: str = None, ip: str = None) -> RefreshSession:
        """Create new refresh session"""
        session = RefreshSession(
            user_id=user_id,
            refresh_token_hash=token_hash,
            device_label=device_label,
            user_agent=user_agent,
            ip=ip
        )
        db.add(session)
        return session
    
    @staticmethod
    def get_by_token_hash(db: Session, token_hash: str) -> RefreshSession | None:
        """Get session by token hash"""
        return db.execute(
            select(RefreshSession).where(RefreshSession.refresh_token_hash == token_hash)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_by_id(db: Session, session_id: int) -> RefreshSession | None:
        """Get session by ID"""
        return db.execute(
            select(RefreshSession).where(RefreshSession.id == session_id)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_active_for_user(db: Session, user_id: uuid.UUID) -> list[RefreshSession]:
        """Get all active sessions for user"""
        return db.execute(
            select(RefreshSession).where(
                (RefreshSession.user_id == user_id) & 
                (RefreshSession.revoked_at.is_(None))
            )
        ).scalars().all()
    
    @staticmethod
    def revoke(db: Session, session: RefreshSession) -> RefreshSession:
        """Revoke a refresh session"""
        from datetime import datetime, timezone
        session.revoked_at = datetime.now(timezone.utc)
        return session
    
    @staticmethod
    def revoke_all_for_user(db: Session, user_id: uuid.UUID) -> int:
        """Revoke all refresh sessions for a user - returns count"""
        from datetime import datetime, timezone
        sessions = RefreshTokenRepository.get_active_for_user(db, user_id)
        count = len(sessions)
        for session in sessions:
            session.revoked_at = datetime.now(timezone.utc)
        return count
    
    @staticmethod
    def update_last_used(db: Session, session: RefreshSession) -> RefreshSession:
        """Update last used timestamp"""
        from datetime import datetime, timezone
        session.last_used_at = datetime.now(timezone.utc)
        return session
