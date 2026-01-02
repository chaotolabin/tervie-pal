# Profile Repository
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.auth import Profile
import uuid


class ProfileRepository:
    """Repository for Profile entity operations"""
    
    @staticmethod
    def create(db: Session, user_id: uuid.UUID, full_name: str = None, 
               gender: str = None, date_of_birth = None, height_cm_default: float = None) -> Profile:
        """Create user profile"""
        profile = Profile(
            user_id=user_id,
            full_name=full_name,
            gender=gender,
            date_of_birth=date_of_birth,
            height_cm_default=height_cm_default
        )
        db.add(profile)
        return profile
