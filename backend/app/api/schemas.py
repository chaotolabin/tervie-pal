# Pydantic schemas for request/response validation
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
import uuid


# ==================== Auth Schemas ====================
class RegisterRequest(BaseModel):
    """Request body for registration"""
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Request body for login"""
    email_or_username: str
    password: str = Field(..., min_length=8, max_length=128)
    device_label: Optional[str] = None


class RefreshRequest(BaseModel):
    """Request body for token refresh"""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Request body for logout"""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Request body for forgot password"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body for reset password"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    """Request body for change password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ==================== User/Profile Schemas ====================
class UserPublic(BaseModel):
    """Public user info"""
    id: uuid.UUID
    username: str
    email: str
    role: str  # UserRole enum: "user" or "admin"

    class Config:
        from_attributes = True


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


class UserMeResponse(BaseModel):
    """Response for GET /users/me"""
    user: UserPublic
    profile: Profile


# ==================== Auth Response Schemas ====================
class AuthTokensResponse(BaseModel):
    """Response for register/login"""
    user: UserPublic
    access_token: str
    refresh_token: str


class RefreshResponse(BaseModel):
    """Response for token refresh"""
    access_token: str
    refresh_token: str


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str


class GenericMessageResponse(BaseModel):
    """Generic success message"""
    message: str


# ==================== Session Schemas ====================
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


# ==================== Settings Schemas ====================
class UserRolePatchRequest(BaseModel):
    """Request to update user role (admin only)"""
    role: str  # "user" or "admin"
