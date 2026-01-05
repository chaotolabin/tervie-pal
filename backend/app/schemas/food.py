"""
Pydantic schemas cho Foods module
- Request schemas: Validate dữ liệu từ client
- Response schemas: Format dữ liệu trả về client
"""
from typing import Optional, List
from datetime import datetime
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


# ===== Nested Schemas =====

class FoodPortionCreate(BaseModel):
    """Schema để tạo portion mới"""
    amount: Decimal = Field(
        ...,
        gt=0,
        description="Số lượng (vd: 1, 0.5)",
        example=1.0
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Đơn vị (vd: cup, tbsp, piece)",
        example="cup"
    )
    grams: Decimal = Field(
        ...,
        gt=0,
        description="Quy đổi ra grams",
        example=240.0
    )

    @field_validator('amount', 'grams')
    @classmethod
    def validate_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Giá trị phải lớn hơn 0")
        return v


class FoodPortionResponse(BaseModel):
    """Schema cho portion trong response"""
    id: int = Field(..., description="ID portion")
    amount: Decimal = Field(..., description="Số lượng")
    unit: str = Field(..., description="Đơn vị")
    grams: Decimal = Field(..., description="Quy đổi ra grams")

    class Config:
        from_attributes = True


class FoodNutrientCreate(BaseModel):
    """Schema để tạo/update nutrient"""
    nutrient_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tên chất dinh dưỡng (vd: calories, protein)",
        example="calories"
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Đơn vị (vd: kcal, g, mg)",
        example="kcal"
    )
    amount_per_100g: Decimal = Field(
        ...,
        ge=0,
        description="Lượng chất dinh dưỡng trên 100g",
        example=150.5
    )

    @field_validator('amount_per_100g')
    @classmethod
    def validate_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Giá trị không được âm")
        return v

    @field_validator("nutrient_name", "unit")
    def normalize(cls, v):
        return v.strip().lower()


class FoodNutrientResponse(BaseModel):
    """Schema cho nutrient trong response"""
    nutrient_name: str = Field(..., description="Tên chất dinh dưỡng")
    unit: str = Field(..., description="Đơn vị")
    amount_per_100g: Decimal = Field(..., description="Lượng per 100g")

    class Config:
        from_attributes = True


# ===== Main Food Schemas =====

class FoodListItem(BaseModel):
    """Schema cho food item trong search results"""
    id: int = Field(..., description="ID thực phẩm")
    name: str = Field(..., description="Tên thực phẩm")
    food_group: Optional[str] = Field(None, description="Nhóm thực phẩm")
    owner_user_id: Optional[uuid.UUID] = Field(None, description="NULL = global, có giá trị = custom")
    source_code: Optional[str] = Field(None, description="Mã nguồn từ dataset")

    class Config:
        from_attributes = True


class FoodSearchResponse(BaseModel):
    """Schema cho kết quả search foods"""
    items: List[FoodListItem] = Field(..., description="Danh sách foods")
    next_cursor: Optional[str] = Field(None, description="Cursor cho trang tiếp theo")

    class Config:
        from_attributes = True


class FoodDetail(BaseModel):
    """Schema cho food detail (bao gồm portions và nutrients)"""
    id: int = Field(..., description="ID thực phẩm")
    owner_user_id: Optional[uuid.UUID] = Field(None, description="NULL = global")
    source_code: Optional[str] = Field(None, description="Mã nguồn")
    name: str = Field(..., description="Tên thực phẩm")
    food_group: Optional[str] = Field(None, description="Nhóm thực phẩm")
    portions: List[FoodPortionResponse] = Field(..., description="Danh sách portions")
    nutrients: List[FoodNutrientResponse] = Field(..., description="Danh sách nutrients")
    is_contribution: bool = Field(default=False, description="Có đóng góp cho cộng đồng không")
    contribution_status: Optional[str] = Field(None, description="Trạng thái đóng góp")
    created_at: Optional[datetime] = Field(None, description="Ngày tạo")
    creator_username: Optional[str] = Field(None, description="Tên người tạo")
    creator_email: Optional[str] = Field(None, description="Email người tạo")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FoodCreateRequest(BaseModel):
    """Schema cho POST /foods - Tạo custom food mới"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Tên thực phẩm",
        example="Cơm trắng tự nấu"
    )
    food_group: Optional[str] = Field(
        None,
        max_length=200,
        description="Nhóm thực phẩm",
        example="Grains"
    )
    source_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Mã nguồn (nếu có)",
        example="CUSTOM001"
    )
    portions: List[FoodPortionCreate] = Field(
        default_factory=list,
        description="Danh sách portions (optional)",
        example=[]
    )
    nutrients: List[FoodNutrientCreate] = Field(
        ...,
        min_length=1,
        description="Danh sách nutrients (bắt buộc ít nhất 1)",
        example=[
            {"nutrient_name": "calories", "unit": "kcal", "amount_per_100g": 130.0},
            {"nutrient_name": "protein", "unit": "g", "amount_per_100g": 2.7}
        ]
    )
    is_contribution: bool = Field(
        default=False,
        description="Có đóng góp cho cộng đồng không"
    )

    @field_validator('nutrients')
    @classmethod
    def validate_nutrients_not_empty(cls, v: List[FoodNutrientCreate]) -> List[FoodNutrientCreate]:
        if not v:
            raise ValueError("Phải có ít nhất 1 nutrient")
        return v


class FoodPatchRequest(BaseModel):
    """Schema cho PATCH /foods/{id} - Cập nhật food"""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Tên thực phẩm mới"
    )
    food_group: Optional[str] = Field(
        None,
        max_length=200,
        description="Nhóm thực phẩm mới"
    )
    portions: Optional[List[FoodPortionCreate]] = Field(
        None,
        description="Danh sách portions mới (sẽ thay thế hoàn toàn list cũ)"
    )
    nutrients: Optional[List[FoodNutrientCreate]] = Field(
        None,
        description="Danh sách nutrients mới (sẽ thay thế hoàn toàn list cũ)"
    )

    @field_validator('nutrients')
    @classmethod
    def validate_nutrients_if_provided(cls, v: Optional[List[FoodNutrientCreate]]) -> Optional[List[FoodNutrientCreate]]:
        if v is not None and len(v) == 0:
            raise ValueError("Nếu cung cấp nutrients thì phải có ít nhất 1 item")
        return v