# Auth related schemas
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
import uuid


class RegisterRequest(BaseModel):
    """Request body for registration (OLD - for backward compatibility)"""
    # Step 5: Basic auth
    username: str = Field(..., min_length=3, max_length=32, description="Tên đăng nhập")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=8, max_length=128, description="Mật khẩu")
    
    # Step 1: Profile info
    full_name: str = Field(..., min_length=1, max_length=255, description="Họ và tên")
    gender: str = Field(..., description="Giới tính: 'male' hoặc 'female'")
    date_of_birth: date = Field(..., description="Ngày sinh (YYYY-MM-DD)")
    
    # Step 4: Biometric
    height_cm: Decimal = Field(..., gt=0, decimal_places=2, description="Chiều cao (cm)")
    weight_kg: Decimal = Field(..., gt=0, decimal_places=2, description="Cân nặng (kg)")
    goal_weight_kg: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Cân nặng mục tiêu (kg)")
    
    # Step 2: Goal type
    goal_type: str = Field(..., description="Loại mục tiêu: lose_weight, gain_weight, maintain_weight, build_muscle, improve_health")
    
    # Step 3: Baseline activity level (bắt buộc)
    baseline_activity: str = Field(..., description="Mức hoạt động: sedentary, low_active, moderately_active, very_active, extremely_active")
    
    # Weekly goal (bắt buộc)
    weekly_goal: float = Field(..., description="Mục tiêu thay đổi cân nặng: 0.25 hoặc 0.5 kg/tuần")
    
    # Additional
    weekly_exercise_min: Optional[int] = Field(None, ge=0, description="Phút vận động/tuần")


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


class UserPublic(BaseModel):
    """Public user info"""
    id: uuid.UUID
    username: str
    email: str
    role: str  # UserRole enum: "user" or "admin"

    class Config:
        from_attributes = True


class AuthTokensResponse(BaseModel):
    """Response for register/login"""
    user: UserPublic
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # OAuth2 standard


class RefreshResponse(BaseModel):
    """Response for token refresh"""
    access_token: str
    refresh_token: str
