"""
Pydantic schemas cho Daily Logs (Food & Exercise tracking)
- Request schemas: Validate dữ liệu từ client
- Response schemas: Format dữ liệu trả về client
"""
from typing import Optional, List
import uuid
from datetime import datetime
from datetime import date as date_type
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.models.log import MealType


# ==================== FOOD LOG SCHEMAS ====================

class FoodLogItemCreate(BaseModel):
    """Schema để tạo 1 món ăn trong bữa ăn"""
    food_id: int = Field(
        ...,
        gt=0,
        description="ID của food từ bảng foods",
        example=1
    )
    portion_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID của portion (nếu dùng portion có sẵn)",
        example=5
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Số lượng (vd: 2 cups, 1.5 servings)",
        example=2.0
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Đơn vị (vd: grams, cups, servings)",
        example="cup"
    )
    grams: Decimal = Field(
        ...,
        gt=0,
        description="Quy đổi về grams để tính dinh dưỡng",
        example=200.0
    )

    @field_validator('quantity', 'grams')
    @classmethod
    def validate_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Giá trị phải lớn hơn 0")
        return v


class FoodLogItemResponse(BaseModel):
    """Schema cho món ăn trong response"""
    id: int = Field(..., description="ID của log item")
    entry_id: int = Field(..., description="ID của entry (bữa ăn)")
    food_id: int = Field(..., description="ID food")
    portion_id: Optional[int] = Field(None, description="ID portion")
    quantity: Decimal = Field(..., description="Số lượng")
    unit: str = Field(..., description="Đơn vị")
    grams: Decimal = Field(..., description="Grams thực tế")
    
    # Snapshot - dinh dưỡng đã tính cho số lượng này
    calories: Optional[Decimal] = Field(None, description="Calo của món (đã tính theo grams)")
    protein_g: Optional[Decimal] = Field(None, description="Protein (g)")
    carbs_g: Optional[Decimal] = Field(None, description="Carbs (g)")
    fat_g: Optional[Decimal] = Field(None, description="Fat (g)")

    class Config:
        from_attributes = True


class FoodLogEntryCreate(BaseModel):
    """Schema để tạo bữa ăn (entry + items)"""
    logged_at: datetime = Field(
        ...,
        description="Thời điểm log bữa ăn (client gửi với timezone)",
        example="2023-10-27T08:00:00+07:00"
    )
    meal_type: MealType = Field(
        ...,
        description="Loại bữa ăn: breakfast, lunch, dinner, snacks",
        example="breakfast"
    )
    items: List[FoodLogItemCreate] = Field(
        ...,
        min_length=1,
        description="Danh sách món ăn trong bữa",
        example=[
            {
                "food_id": 1,
                "quantity": 2,
                "unit": "slice",
                "grams": 60
            }
        ]
    )

    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v: List[FoodLogItemCreate]) -> List[FoodLogItemCreate]:
        if not v:
            raise ValueError("Bữa ăn phải có ít nhất 1 món")
        return v


class FoodLogEntryResponse(BaseModel):
    """Schema cho bữa ăn trong response"""
    id: int = Field(..., description="ID của entry")
    user_id: uuid.UUID = Field(..., description="UUID của user")
    logged_at: datetime = Field(..., description="Thời điểm log")
    meal_type: MealType = Field(..., description="Loại bữa ăn")
    
    # Tổng hợp dinh dưỡng của cả bữa
    total_calories: Decimal = Field(..., description="Tổng calo của bữa ăn")
    total_protein_g: Decimal = Field(..., description="Tổng protein (g)")
    total_carbs_g: Decimal = Field(..., description="Tổng carbs (g)")
    total_fat_g: Decimal = Field(..., description="Tổng fat (g)")
    
    created_at: datetime = Field(..., description="Thời điểm tạo record")
    updated_at: Optional[datetime] = Field(None, description="Thời điểm cập nhật")
    deleted_at: Optional[datetime] = Field(None, description="Thời điểm xóa (soft delete)")
    
    # Danh sách món ăn chi tiết
    items: List[FoodLogItemResponse] = Field(default_factory=list, description="Chi tiết các món")

    class Config:
        from_attributes = True


class FoodLogItemUpdate(BaseModel):
    """Schema để update món ăn trong bữa ăn (chỉ quantity và grams)"""
    quantity: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Số lượng mới"
    )
    unit: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="Đơn vị mới"
    )
    grams: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Grams mới (dùng để tính lại dinh dưỡng)"
    )

    @field_validator('quantity', 'grams')
    @classmethod
    def validate_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Giá trị phải lớn hơn 0")
        return v


class FoodLogEntryPatch(BaseModel):
    """Schema để update bữa ăn (chỉ cập nhật meal_type và logged_at)"""
    logged_at: Optional[datetime] = Field(
        None,
        description="Thời điểm log bữa ăn mới"
    )
    meal_type: Optional[MealType] = Field(
        None,
        description="Loại bữa ăn mới"
    )

    class Config:
        # Cho phép partial update (tất cả field đều optional)
        pass


# ==================== EXERCISE LOG SCHEMAS ====================

class ExerciseLogItemCreate(BaseModel):
    """Schema để tạo 1 bài tập trong buổi tập"""
    exercise_id: int = Field(
        ...,
        gt=0,
        description="ID của exercise từ bảng exercises",
        example=10
    )
    duration_min: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Thời gian tập (phút)",
        example=30.0
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Ghi chú thêm (tùy chọn)",
        example="Cảm thấy mệt"
    )

    @field_validator('duration_min')
    @classmethod
    def validate_duration_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Thời gian tập phải lớn hơn 0")
        return v


class ExerciseLogItemResponse(BaseModel):
    """Schema cho bài tập trong response"""
    id: int = Field(..., description="ID của log item")
    entry_id: int = Field(..., description="ID của entry (buổi tập)")
    exercise_id: int = Field(..., description="ID exercise")
    duration_min: Optional[Decimal] = Field(None, description="Thời gian tập (phút)")
    
    # Snapshot
    met_value_snapshot: Optional[Decimal] = Field(None, description="MET value tại thời điểm log")
    calories: Optional[Decimal] = Field(None, description="Calo tiêu hao (đã tính)")
    
    notes: Optional[str] = Field(None, description="Ghi chú")

    class Config:
        from_attributes = True


class ExerciseLogEntryCreate(BaseModel):
    """Schema để tạo buổi tập (entry + items)"""
    logged_at: datetime = Field(
        ...,
        description="Thời điểm log buổi tập (client gửi với timezone)",
        example="2023-10-27T18:00:00+07:00"
    )
    items: List[ExerciseLogItemCreate] = Field(
        ...,
        min_length=1,
        description="Danh sách bài tập trong buổi",
        example=[
            {
                "exercise_id": 10,
                "duration_min": 30.0,
                "notes": "Running at moderate pace"
            }
        ]
    )

    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v: List[ExerciseLogItemCreate]) -> List[ExerciseLogItemCreate]:
        if not v:
            raise ValueError("Buổi tập phải có ít nhất 1 bài tập")
        return v


class ExerciseLogEntryResponse(BaseModel):
    """Schema cho buổi tập trong response"""
    id: int = Field(..., description="ID của entry")
    user_id: uuid.UUID = Field(..., description="UUID của user")
    logged_at: datetime = Field(..., description="Thời điểm log")
    
    # Tổng hợp
    total_calories: Decimal = Field(..., description="Tổng calo tiêu hao")
    
    created_at: datetime = Field(..., description="Thời điểm tạo record")
    updated_at: Optional[datetime] = Field(None, description="Thời điểm cập nhật")
    deleted_at: Optional[datetime] = Field(None, description="Thời điểm xóa (soft delete)")
    
    # Danh sách bài tập chi tiết
    items: List[ExerciseLogItemResponse] = Field(default_factory=list, description="Chi tiết các bài tập")

    class Config:
        from_attributes = True


class ExerciseLogItemUpdate(BaseModel):
    """Schema để update bài tập trong buổi tập (chỉ duration và notes)"""
    duration_min: Decimal = Field(
        None,
        gt=0,
        description="Thời gian tập mới (phút)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Ghi chú mới"
    )

    @field_validator('duration_min')
    @classmethod
    def validate_duration_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Thời gian tập phải lớn hơn 0")
        return v


class ExerciseLogEntryPatch(BaseModel):
    """Schema để update buổi tập (chỉ cập nhật logged_at)"""
    logged_at: Optional[datetime] = Field(
        None,
        description="Thời điểm log buổi tập mới"
    )

    class Config:
        # Cho phép partial update
        pass


# ==================== DAILY SUMMARY SCHEMAS ====================

class DailyNutritionSummary(BaseModel):
    """Tổng hợp dinh dưỡng trong ngày"""
    date: date_type = Field(..., description="Ngày (YYYY-MM-DD)", example="2023-10-27")
    total_calories_consumed: Decimal = Field(..., description="Tổng calo ăn vào")
    total_calories_burned: Decimal = Field(..., description="Tổng calo tiêu hao")
    net_calories: Decimal = Field(..., description="Calo ròng (consumed - burned)")
    total_protein_g: Decimal = Field(..., description="Tổng protein (g)")
    total_carbs_g: Decimal = Field(..., description="Tổng carbs (g)")
    total_fat_g: Decimal = Field(..., description="Tổng fat (g)")


class DailyLogsResponse(BaseModel):
    """Response cho tất cả logs trong 1 ngày"""
    date: date_type = Field(..., description="Ngày (YYYY-MM-DD)")
    food_logs: List[FoodLogEntryResponse] = Field(default_factory=list, description="Các bữa ăn")
    exercise_logs: List[ExerciseLogEntryResponse] = Field(default_factory=list, description="Các buổi tập")
    summary: DailyNutritionSummary = Field(..., description="Tổng kết dinh dưỡng ngày")