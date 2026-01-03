"""
Pydantic schemas cho Goals module
- Request schemas: Validate dữ liệu từ client
- Response schemas: Format dữ liệu trả về client

NOTE: Công thức tính daily_calorie và macros được tự động tính từ server,
người dùng không thể nhập trực tiếp các giá trị này.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class GoalType(str, Enum):
    """Các loại mục tiêu hỗ trợ"""
    LOSE_WEIGHT = "lose_weight"
    GAIN_WEIGHT = "gain_weight"
    MAINTAIN_WEIGHT = "maintain_weight"
    BUILD_MUSCLE = "build_muscle"
    IMPROVE_HEALTH = "improve_health"


class ActivityLevel(str, Enum):
    """Mức độ hoạt động để tính TDEE"""
    SEDENTARY = "sedentary"
    LOW_ACTIVE = "low_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class GoalCreateRequest(BaseModel):
    """
    Schema cho PUT /goals - Tạo mới hoặc cập nhật toàn bộ goal
    Server sẽ tự động tính daily_calorie_target và macros từ:
    - Profile: gender, date_of_birth, baseline_activity
    - Latest Biometrics: weight_kg, height_cm
    - Goal settings: goal_type, weekly_goal, target_weight_kg
    """
    goal_type: GoalType = Field(
        ...,
        description="Loại mục tiêu: lose_weight, gain_weight, maintain_weight, build_muscle, improve_health"
    )
    
    baseline_activity: ActivityLevel = Field(
        ...,
        description="Mức độ hoạt động cơ bản để tính TDEE"
    )
    
    target_weight_kg: Optional[float] = Field(
        None,
        gt=0,
        le=700,
        description="Cân nặng mục tiêu (kg) - chỉ cần khi lose_weight hoặc gain_weight"
    )
    
    weekly_goal: Optional[float] = Field(
        0.5,
        gt=0,
        le=1.0,
        description="Mục tiêu kg/tuần (0.25 - 1.0). Chỉ dùng cho lose_weight, gain_weight, build_muscle"
    )
    
    weekly_exercise_min: Optional[int] = Field(
        None,
        ge=0,
        le=10080,  # Max = 7 days * 24 hours * 60 min
        description="Số phút tập luyện mục tiêu mỗi tuần (ví dụ: 150)"
    )

    @field_validator('target_weight_kg')
    @classmethod
    def validate_target_weight(cls, v: Optional[float], info) -> Optional[float]:
        """target_weight_kg bắt buộc khi goal_type là lose_weight hoặc gain_weight"""
        # Validator sẽ được check sau khi tất cả values đã parse
        return v


class GoalPatchRequest(BaseModel):
    """
    Schema cho PATCH /goals - Cập nhật một phần goal
    Chỉ update các field được gửi, giữ nguyên các field khác.
    Server sẽ tự động recalculate daily_calorie_target và macros nếu có thay đổi ảnh hưởng.
    """
    goal_type: Optional[GoalType] = Field(
        None,
        description="Loại mục tiêu mới"
    )
    
    baseline_activity: Optional[ActivityLevel] = Field(
        None,
        description="Mức độ hoạt động mới"
    )
    
    target_weight_kg: Optional[float] = Field(
        None,
        gt=0,
        le=700,
        description="Cân nặng mục tiêu mới"
    )
    
    weekly_goal: Optional[float] = Field(
        None,
        gt=0,
        le=1.0,
        description="Mục tiêu kg/tuần mới"
    )
    
    weekly_exercise_min: Optional[int] = Field(
        None,
        ge=0,
        le=10080,
        description="Số phút tập luyện mục tiêu mỗi tuần"
    )


class GoalResponse(BaseModel):
    """Schema response cho goal - Trả về đầy đủ thông tin goal hiện tại"""
    user_id: uuid.UUID = Field(..., description="UUID của user")
    goal_type: str = Field(..., description="Loại mục tiêu")
    baseline_activity: Optional[str] = Field(None, description="Mức độ hoạt động")
    weekly_goal: Optional[Decimal] = Field(None, description="Mục tiêu kg/tuần")
    target_weight_kg: Optional[Decimal] = Field(None, description="Cân nặng mục tiêu (kg)")
    daily_calorie_target: Decimal = Field(..., description="Calo mục tiêu mỗi ngày (kcal)")
    protein_grams: Optional[Decimal] = Field(None, description="Protein mục tiêu (grams)")
    fat_grams: Optional[Decimal] = Field(None, description="Fat mục tiêu (grams)")
    carb_grams: Optional[Decimal] = Field(None, description="Carbs mục tiêu (grams)")
    weekly_exercise_min: Optional[int] = Field(None, description="Phút tập luyện mục tiêu/tuần")
    created_at: datetime = Field(..., description="Thời điểm tạo")
    updated_at: datetime = Field(..., description="Thời điểm cập nhật")

    model_config = {"from_attributes": True}


class GoalCalculateRequest(BaseModel):
    """
    Schema cho POST /goals/calculate - Tính toán preview (không lưu)
    Cho phép user xem trước daily_calorie và macros trước khi commit goal
    """
    goal_type: GoalType = Field(..., description="Loại mục tiêu")
    baseline_activity: ActivityLevel = Field(..., description="Mức độ hoạt động")
    weekly_goal: Optional[float] = Field(
        0.5,
        gt=0,
        le=1.0,
        description="Mục tiêu kg/tuần"
    )


class GoalCalculateResponse(BaseModel):
    """Schema response cho calculate preview"""
    # Input echo
    goal_type: str
    baseline_activity: str
    weekly_goal: float
    
    # Biometrics used
    weight_kg: float = Field(..., description="Cân nặng hiện tại từ latest biometrics")
    height_cm: float = Field(..., description="Chiều cao hiện tại từ latest biometrics")
    
    # Profile data
    gender: str
    age_years: int
    
    # Calculated values
    bmr: float = Field(..., description="Basal Metabolic Rate (kcal/day)")
    tdee: float = Field(..., description="Total Daily Energy Expenditure (kcal/day)")
    daily_calorie_target: float = Field(..., description="Calo mục tiêu (kcal/day)")
    protein_grams: float = Field(..., description="Protein mục tiêu (grams)")
    fat_grams: float = Field(..., description="Fat mục tiêu (grams)")
    carb_grams: float = Field(..., description="Carbs mục tiêu (grams)")
