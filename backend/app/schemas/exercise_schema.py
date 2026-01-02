"""
Pydantic Schemas cho Exercise Module
Chuyển đổi từ OpenAPI spec thành Pydantic models
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
import uuid


# ===== Request Schemas =====

class ExerciseCreateRequest(BaseModel):
    """Schema cho tạo exercise mới"""
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        example="Running, 5 mph (12 min/mile)"
    )
    major_heading: Optional[str] = Field(
        None,
        max_length=200,
        example="Running"
    )
    met_value: Decimal = Field(
        ...,
        gt=0,
        le=99.99,
        decimal_places=2,
        example=8.3
    )


class ExercisePatchRequest(BaseModel):
    """Schema cho update exercise (partial update)"""
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500
    )
    major_heading: Optional[str] = Field(
        None,
        max_length=200
    )
    met_value: Optional[Decimal] = Field(
        None,
        gt=0,
        le=99.99,
        decimal_places=2
    )


# ===== Response Schemas =====

class ExerciseResponse(BaseModel):
    """Schema cho response exercise detail"""
    id: int
    owner_user_id: Optional[uuid.UUID] = None
    activity_code: Optional[str] = None
    major_heading: Optional[str] = None
    description: str
    met_value: Decimal

    class Config:
        from_attributes = True  # Cho phép convert từ SQLAlchemy model


class ExerciseListItem(ExerciseResponse):
    """Schema cho item trong search list (giống ExerciseResponse)"""
    pass


class ExerciseSearchResponse(BaseModel):
    """Schema cho kết quả search với pagination"""
    items: List[ExerciseListItem]
    next_cursor: Optional[str] = None

    class Config:
        from_attributes = True