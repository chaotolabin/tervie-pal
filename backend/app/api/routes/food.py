"""
Router cho Foods Module - API Endpoints
Xử lý HTTP requests/responses, gọi Service layer cho business logic
"""
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.services.foods import FoodService, FoodPortionService, FoodNutrientService
from app.schemas.food_schema import (
    FoodSearchResponse,
    FoodListItem,
    FoodCreateRequest,
    FoodDetail,
    FoodPatchRequest,
    FoodPortionCreate, FoodPortionResponse,
    FoodNutrientCreate, FoodNutrientResponse
)


# Tạo router với prefix và tags
router = APIRouter(
    prefix="/foods",
    tags=["Foods"]
)


@router.get(
    "/search",
    response_model=FoodSearchResponse,
    summary="Search foods",
    description="Tìm kiếm foods theo tên. Trả về global foods + custom foods của user."
)
def search_foods(
    q: Annotated[str, Query(
        min_length=1,
        description="Từ khóa tìm kiếm"
    )],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(
        ge=1,
        le=100,
        description="Số lượng kết quả tối đa"
    )] = 20,
    cursor: Annotated[Optional[str], Query(
        description="Cursor cho pagination (ID của food cuối cùng ở trang trước)"
    )] = None
) -> FoodSearchResponse:
    """
    GET /foods/search?q=chicken&limit=20&cursor=123
    
    Args:
        q: Từ khóa tìm kiếm (bắt buộc)
        db: Database session (auto-injected)
        current_user: User hiện tại (auto-injected từ JWT)
        limit: Số lượng kết quả tối đa (default 20, max 100)
        cursor: Cursor cho pagination (optional)
    
    Returns:
        FoodSearchResponse: Danh sách foods + next_cursor
    
    Example:
        GET /foods/search?q=rice
        GET /foods/search?q=chicken&limit=50&cursor=456
    """
    foods, next_cursor = FoodService.search_foods(
        db=db,
        user_id=current_user.id,
        query=q,
        limit=limit,
        cursor=cursor
    )
    
    return FoodSearchResponse(
        items=[FoodListItem.model_validate(food) for food in foods],
        next_cursor=next_cursor
    )


@router.post(
    "",
    response_model=FoodDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create custom food",
    description="Tạo custom food mới cho user hiện tại. Bao gồm portions và nutrients."
)
def create_food(
    data: FoodCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> FoodDetail:
    """
    POST /foods
    
    Args:
        data: Request body với name, food_group, portions, nutrients
        db: Database session (auto-injected)
        current_user: User hiện tại (auto-injected từ JWT)
    
    Returns:
        FoodDetail: Food vừa tạo
    
    Raises:
        401 Unauthorized: Nếu chưa login
        422 Validation Error: Nếu dữ liệu không hợp lệ
    
    Example Request Body:
        {
            "name": "Cơm trắng tự nấu",
            "food_group": "Grains",
            "portions": [
                {"amount": 1, "unit": "cup", "grams": 158}
            ],
            "nutrients": [
                {"nutrient_name": "calories", "unit": "kcal", "amount_per_100g": 130},
                {"nutrient_name": "protein", "unit": "g", "amount_per_100g": 2.7}
            ]
        }
    """
    db_food = FoodService.create_food(db, current_user.id, data)
    return FoodDetail.model_validate(db_food)


@router.get(
    "/{food_id}",
    response_model=FoodDetail,
    summary="Get food detail",
    description="Lấy chi tiết food theo ID (bao gồm portions và nutrients)."
)
def get_food(
    food_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> FoodDetail:
    """
    GET /foods/{food_id}
    
    Args:
        food_id: ID của food
        db: Database session
        current_user: User hiện tại
    
    Returns:
        FoodDetail: Chi tiết food
    
    Raises:
        404 Not Found: Nếu food không tồn tại hoặc không có quyền xem
    
    Example:
        GET /foods/{food_id}
    """
    db_food = FoodService.get_food_by_id(db, food_id, current_user.id)
    return FoodDetail.model_validate(db_food)


@router.patch(
    "/{food_id}",
    response_model=FoodDetail,
    summary="Update food metadata",
    description="Cập nhật thông tin cơ bản của food (name, food_group). Để update portions/nutrients, dùng endpoints riêng."
)
def update_food(
    food_id: int,
    data: FoodPatchRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> FoodDetail:
    """
    PATCH /foods/{food_id}
    
    Chỉ cập nhật name và food_group.
    Để cập nhật portions/nutrients, dùng:
    - POST/PATCH/DELETE /foods/{food_id}/portions/{portion_id}
    - POST/PATCH/DELETE /foods/{food_id}/nutrients/{nutrient_name}
    
    Args:
        food_id: ID của food cần update
        data: Dữ liệu cần update (name, food_group)
        db: Database session
        user_id: UUID của user hiện tại
    
    Returns:
        FoodDetail: Food sau khi update
    
    Raises:
        403 Forbidden: Nếu không phải owner hoặc admin
        404 Not Found: Nếu food không tồn tại
        422 Validation Error: Nếu dữ liệu không hợp lệ
    
    Example Request Body (partial update):
        {
            "name": "Cơm trắng nấu mới"
        }
    """
    db_food = FoodService.update_food(db, food_id, current_user.id, data)
    return FoodDetail.model_validate(db_food)


@router.delete(
    "/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete food",
    description="Xóa custom food (soft delete). Chỉ owner hoặc admin mới được phép."
)
def delete_food(
    food_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    DELETE /foods/{food_id}
    
    Args:
        food_id: ID của food cần xóa
        db: Database session
        current_user: User hiện tại
    
    Raises:
        403 Forbidden: Nếu không phải owner hoặc admin
        404 Not Found: Nếu food không tồn tại
    
    Example:
        DELETE /foods/123
    """
    FoodService.delete_food(db, food_id, current_user.id)
    # No content response (204)

# ===== Food Portions Endpoints =====

@router.post(
    "/{food_id}/portions",
    response_model=FoodPortionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add portion to food",
    description="Thêm portion mới cho food"
)
def create_food_portion(
    food_id: int,
    data: FoodPortionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> FoodPortionResponse:
    """
    POST /foods/{food_id}/portions
    
    Args:
        food_id: ID của food
        data: Thông tin portion (amount, unit, grams)
        db: Database session
        current_user: User hiện tại
    
    Returns:
        FoodPortionResponse: Portion vừa tạo
    
    Example:
        POST /foods/123/portions
        {
            "amount": 1,
            "unit": "cup",
            "grams": 240
        }
    """
    db_portion = FoodPortionService.create_portion(db, food_id, current_user.id, data)
    return FoodPortionResponse.model_validate(db_portion)


@router.get(
    "/{food_id}/portions",
    response_model=List[FoodPortionResponse],
    summary="Get food portions",
    description="Lấy danh sách portions của food"
)
def get_food_portions(
    food_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> List[FoodPortionResponse]:
    """
    GET /foods/{food_id}/portions
    
    Args:
        food_id: ID của food
        db: Database session
        current_user: User hiện tại
    
    Returns:
        List[FoodPortionResponse]: Danh sách portions
    """
    portions = FoodPortionService.get_portions_by_food_id(db, food_id, current_user.id)
    return [FoodPortionResponse.model_validate(p) for p in portions]


@router.patch(
    "/{food_id}/portions/{portion_id}",
    response_model=FoodPortionResponse,
    summary="Update portion",
    description="Cập nhật portion"
)
def update_food_portion(
    food_id: int,
    portion_id: int,
    data: FoodPortionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> FoodPortionResponse:
    """
    PATCH /foods/{food_id}/portions/{portion_id}
    
    Args:
        food_id: ID của food
        portion_id: ID của portion
        data: Thông tin mới
        db: Database session
        current_user: User hiện tại
    
    Returns:
        FoodPortionResponse: Portion sau khi update
    """
    db_portion = FoodPortionService.update_portion(db, food_id, portion_id, current_user.id, data)
    return FoodPortionResponse.model_validate(db_portion)


@router.delete(
    "/{food_id}/portions/{portion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete portion",
    description="Xóa portion"
)
def delete_food_portion(
    food_id: int,
    portion_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    DELETE /foods/{food_id}/portions/{portion_id}
    
    Args:
        food_id: ID của food
        portion_id: ID của portion
        db: Database session
        current_user: User hiện tại
    """
    FoodPortionService.delete_portion(db, food_id, portion_id, current_user.id)


# ===== Food Nutrients Endpoints =====

@router.post(
    "/{food_id}/nutrients",
    response_model=FoodNutrientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add nutrient to food",
    description="Thêm nutrient mới cho food"
)
def create_food_nutrient(
    food_id: int,
    data: FoodNutrientCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> FoodNutrientResponse:
    """
    POST /foods/{food_id}/nutrients
    
    Args:
        food_id: ID của food
        data: Thông tin nutrient (nutrient_name, unit, amount_per_100g)
        db: Database session
        current_user: User hiện tại
    
    Returns:
        FoodNutrientResponse: Nutrient vừa tạo
    
    Example:
        POST /foods/123/nutrients
        {
            "nutrient_name": "protein",
            "unit": "g",
            "amount_per_100g": 25.5
        }
    """
    db_nutrient = FoodNutrientService.create_nutrient(db, food_id, current_user.id, data)
    return FoodNutrientResponse.model_validate(db_nutrient)


@router.get(
    "/{food_id}/nutrients",
    response_model=List[FoodNutrientResponse],
    summary="Get food nutrients",
    description="Lấy danh sách nutrients của food"
)
def get_food_nutrients(
    food_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> List[FoodNutrientResponse]:
    """
    GET /foods/{food_id}/nutrients
    
    Args:
        food_id: ID của food
        db: Database session
        current_user: User hiện tại
    
    Returns:
        List[FoodNutrientResponse]: Danh sách nutrients
    """
    nutrients = FoodNutrientService.get_nutrients_by_food_id(db, food_id, current_user.id)
    return [FoodNutrientResponse.model_validate(n) for n in nutrients]


@router.patch(
    "/{food_id}/nutrients/{nutrient_name}",
    response_model=FoodNutrientResponse,
    summary="Update nutrient",
    description="Cập nhật nutrient (unit và amount)"
)
def update_food_nutrient(
    food_id: int,
    nutrient_name: str,
    data: FoodNutrientCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> FoodNutrientResponse:
    """
    PATCH /foods/{food_id}/nutrients/{nutrient_name}
    
    Note: Không thể đổi nutrient_name (vì là primary key)
    
    Args:
        food_id: ID của food
        nutrient_name: Tên nutrient cần update
        data: Thông tin mới (unit, amount_per_100g)
        db: Database session
        current_user: User hiện tại
    
    Returns:
        FoodNutrientResponse: Nutrient sau khi update
    """
    db_nutrient = FoodNutrientService.update_nutrient(db, food_id, nutrient_name, current_user.id, data)
    return FoodNutrientResponse.model_validate(db_nutrient)


@router.delete(
    "/{food_id}/nutrients/{nutrient_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete nutrient",
    description="Xóa nutrient"
)
def delete_food_nutrient(
    food_id: int,
    nutrient_name: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    DELETE /foods/{food_id}/nutrients/{nutrient_name}
    
    Args:
        food_id: ID của food
        nutrient_name: Tên nutrient cần xóa
        db: Database session
        current_user: User hiện tại
    """
    FoodNutrientService.delete_nutrient(db, food_id, nutrient_name.lower(), current_user.id)