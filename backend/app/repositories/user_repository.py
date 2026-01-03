# User Repository - mọi db.query liên quan tới User
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.auth import User, Profile
import uuid


class UserRepository:
    """Repository for User entity operations"""
    
    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
        """Get user by ID"""
        return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        """Get user by email"""
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        """Get user by username"""
        return db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    
    @staticmethod
    def get_by_email_or_username(db: Session, email_or_username: str) -> User | None:
        """Get user by email or username"""
        return db.execute(
            select(User).where(
                (User.email == email_or_username) | (User.username == email_or_username)
            )
        ).scalar_one_or_none()
    
    @staticmethod
    def create(db: Session, **kwargs) -> User:
        """Create new user"""
        user = User(**kwargs)
        db.add(user)
        return user
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination"""
        return db.execute(select(User).offset(skip).limit(limit)).scalars().all()
    
    @staticmethod
    def update(db: Session, user: User, **kwargs) -> User:
        """Update user fields"""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user
