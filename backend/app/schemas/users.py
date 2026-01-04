# User and profile related schemas
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import uuid


class Profile(BaseModel):
    """User profile info"""
    user_id: uuid.UUID
    full_name: Optional[str] = None
    gender: Optional[str] = None  # "male", "female"
    date_of_birth: Optional[str] = None  # ISO date
    height_cm_default: Optional[float] = None

    class Config:
        from_attributes = True


class ProfilePatchRequest(BaseModel):
    """Update profile (partial)"""
    full_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    height_cm_default: Optional[float] = None


class UserPublic(BaseModel):
    """Public user info"""
    id: uuid.UUID
    username: str
    email: str
    role: str  # UserRole enum: "user" or "admin"
    created_at: Optional[datetime] = None  # Ngày tham gia

    class Config:
        from_attributes = True


class UserMeResponse(BaseModel):
    """Response for GET /users/me"""
    user: UserPublic
    profile: Profile


class Session(BaseModel):
    """Refresh session info"""
    id: int
    device_label: Optional[str] = None
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionsListResponse(BaseModel):
    """Response for listing sessions"""
    items: List[Session]


class UserRolePatchRequest(BaseModel):
    """Request to update user role (admin only)"""
    role: str  # "user" or "admin"
