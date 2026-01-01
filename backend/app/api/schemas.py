# Pydantic schemas for request/response validation
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
import uuid


# ==================== Signup Sessions (Multi-step) ====================
class SignupSessionStart(BaseModel):
    """Request: POST /api/v1/signup/sessions - Tạo draft session"""
    pass  # Không cần dữ liệu, server tạo session_id


class SignupSessionUpdateStep1(BaseModel):
    """Request: PATCH /api/v1/signup/sessions/{id} - Step 1: Profile"""
    first_name: str = Field(..., min_length=1, max_length=255, description="Họ và tên")
    date_of_birth: date = Field(..., description="Ngày sinh (YYYY-MM-DD)")
    gender: str = Field(..., description="Giới tính: male, female, other, prefer_not_to_say")


class SignupSessionUpdateStep2(BaseModel):
    """Request: PATCH /api/v1/signup/sessions/{id} - Step 2: Goal Type"""
    goal_type: str = Field(..., description="lose_weight, gain_weight, maintain_weight, build_muscle, improve_health")


class SignupSessionUpdateStep3(BaseModel):
    """Request: PATCH /api/v1/signup/sessions/{id} - Step 3: Activity Level"""
    baseline_activity: str = Field(..., description="sedentary, low_active, moderately_active, very_active, extremely_active")


class SignupSessionUpdateStep4(BaseModel):
    """Request: PATCH /api/v1/signup/sessions/{id} - Step 4: Body Metrics"""
    height_cm: float = Field(..., gt=0, description="Chiều cao (cm)")
    weight_kg: float = Field(..., gt=0, description="Cân nặng (kg)")
    goal_weight_kg: Optional[float] = Field(None, gt=0, description="Cân nặng mục tiêu (kg)")
    weekly_goal: Optional[float] = Field(None, description="Mục tiêu thay đổi cân nặng/tuần (kg)")
    weekly_exercise_min: Optional[int] = Field(None, ge=0, description="Phút vận động/tuần")


class SignupSessionCalculate(BaseModel):
    """Request: POST /api/v1/signup/sessions/{id}/calculate - Tính BMR, TDEE, Calorie"""
    pass  # Server tính từ session data


class SignupSessionUpdateStep5(BaseModel):
    """Request: PATCH /api/v1/signup/sessions/{id} - Step 5: Account"""
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=8, max_length=128, description="Mật khẩu")


class SignupSessionComplete(BaseModel):
    """Request: POST /api/v1/signup/sessions/{id}/complete - Persist to DB"""
    username: str = Field(..., min_length=3, max_length=32, description="Tên đăng nhập")


class SignupSessionStartResponse(BaseModel):
    """Response: POST /api/v1/signup/sessions"""
    session_id: uuid.UUID
    signup_token: str
    current_step: str
    expires_in_hours: int


class SignupSessionUpdateResponse(BaseModel):
    """Response: PATCH steps (Step 1-5) - không cần signup_token"""
    id: uuid.UUID
    first_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    goal_type: Optional[str] = None
    baseline_activity: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal_weight_kg: Optional[float] = None
    weekly_goal: Optional[float] = None
    weekly_exercise_min: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    current_step: str
    calculated_data: Optional[dict] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class SignupSessionResponse(BaseModel):
    """Response: GET session detail"""
    id: uuid.UUID
    signup_token: str
    first_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    goal_type: Optional[str] = None
    baseline_activity: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal_weight_kg: Optional[float] = None
    weekly_goal: Optional[float] = None
    weekly_exercise_min: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    current_step: str
    calculated_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    """Response: Check email/username availability"""
    available: bool
    message: Optional[str] = None


# ==================== Auth Schemas ====================
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
    token_type: str = "Bearer"  # OAuth2 standard


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
