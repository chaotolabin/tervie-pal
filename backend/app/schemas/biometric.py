"""
Pydantic schemas cho Biometrics module
- Request schemas: Validate dữ liệu từ client
- Response schemas: Format dữ liệu trả về client
"""
from datetime import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, Field, field_validator


class BiometricsCreateRequest(BaseModel):
    """Schema cho POST /biometrics - Tạo log mới"""
    logged_at: datetime = Field(
        ...,
        description="Thời điểm đo chỉ số (client gửi)",
        example="2025-12-30T08:00:00Z"
    )
    weight_kg: float = Field(
        ...,
        gt=0,
        le=700,
        description="Cân nặng (kg), phải > 0 và <= 700",
        example=75.5
    )
    height_cm: float = Field(
        ...,
        gt=0,
        le=300,
        description="Chiều cao (cm), phải > 0 và <= 300",
        example=175.0
    )

    @field_validator('weight_kg', 'height_cm')
    @classmethod
    def validate_positive(cls, v: float) -> float:
        """Đảm bảo giá trị dương"""
        if v <= 0:
            raise ValueError("Giá trị phải lớn hơn 0")
        return v


class BiometricsPatchRequest(BaseModel):
    """Schema cho PATCH /biometrics/{id} - Cập nhật log"""
    logged_at: Optional[datetime] = Field(
        None,
        description="Thời điểm đo (có thể update)"
    )
    weight_kg: Optional[float] = Field(
        None,
        gt=0,
        le=700,
        description="Cân nặng mới"
    )
    height_cm: Optional[float] = Field(
        None,
        gt=0,
        le=300,
        description="Chiều cao mới"
    )

    @field_validator('weight_kg', 'height_cm')
    @classmethod
    def validate_positive_if_provided(cls, v: Optional[float]) -> Optional[float]:
        """Nếu có giá trị thì phải dương"""
        if v is not None and v <= 0:
            raise ValueError("Giá trị phải lớn hơn 0")
        return v


class BiometricsLogResponse(BaseModel):
    """Schema cho response - Một record biometrics"""
    id: int = Field(..., description="ID của log")
    user_id: uuid.UUID = Field(..., description="UUID của user (dạng string)")
    logged_at: datetime = Field(..., description="Thời điểm đo")
    weight_kg: float = Field(..., description="Cân nặng (kg)")
    height_cm: float = Field(..., description="Chiều cao (cm)")
    bmi: float = Field(..., description="Chỉ số BMI (tự động tính)")
    created_at: datetime = Field(..., description="Thời điểm tạo record")

    class Config:
        # Cho phép convert từ SQLAlchemy model
        from_attributes = True


class BiometricsListResponse(BaseModel):
    """Schema cho GET /biometrics - List logs"""
    items: List[BiometricsLogResponse] = Field(
        ...,
        description="Danh sách các log biometrics"
    )

    class Config:
        from_attributes = True