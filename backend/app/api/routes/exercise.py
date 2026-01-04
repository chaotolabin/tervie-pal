"""
Router cho Exercise Module - API Endpoints
Xử lý HTTP requests/responses, gọi Service layer cho business logic
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.services.exercise_service import ExerciseService
from app.schemas.exercise import (
    ExerciseSearchResponse,
    ExerciseListItem,
    ExerciseCreateRequest,
    ExerciseResponse,
    ExercisePatchRequest
)


# Tạo router với prefix và tags
router = APIRouter(
    prefix="/exercises",
    tags=["Exercises"]
)


@router.get(
    "/search",
    response_model=ExerciseSearchResponse,
    summary="Search exercises",
    description="Tìm kiếm exercises theo tên. Trả về global exercises + custom exercises của user."
)
def search_exercises(
    q: Annotated[str, Query(
        min_length=1,
        description="Từ khóa tìm kiếm trong description"
    )],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    major_heading: Annotated[Optional[str], Query(
        description="Lọc theo nhóm bài tập (e.g., Running, Swimming)"
    )] = None,
    limit: Annotated[int, Query(
        ge=1,
        le=100,
        description="Số lượng kết quả tối đa"
    )] = 20,
    cursor: Annotated[Optional[str], Query(
        description="Cursor cho pagination (ID của exercise cuối cùng ở trang trước)"
    )] = None
) -> ExerciseSearchResponse:
    """
    GET /exercises/search?q=running&limit=20&cursor=123
    
    Args:
        q: Từ khóa tìm kiếm (bắt buộc)
        db: Database session (auto-injected)
        current_user: User hiện tại (auto-injected từ JWT)
        major_heading: Lọc theo nhóm bài tập (optional)
        limit: Số lượng kết quả tối đa (default 20, max 100)
        cursor: Cursor cho pagination (optional)
    
    Returns:
        ExerciseSearchResponse: Danh sách exercises + next_cursor
    
    Example:
        GET /exercises/search?q=running
        GET /exercises/search?q=swim&major_heading=Swimming&limit=50&cursor=456
    """
    exercises, next_cursor = ExerciseService.search_exercises(
        db=db,
        user_id=current_user.id,
        query=q,
        major_heading=major_heading,
        limit=limit,
        cursor=cursor
    )
    
    return ExerciseSearchResponse(
        items=[ExerciseListItem.model_validate(ex) for ex in exercises],
        next_cursor=next_cursor
    )


@router.post(
    "",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create custom exercise",
    description="Tạo custom exercise mới cho user hiện tại."
)
def create_exercise(
    data: ExerciseCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> ExerciseResponse:
    """
    POST /exercises
    
    Args:
        data: Request body với description, major_heading, met_value
        db: Database session (auto-injected)
        current_user: User hiện tại (auto-injected từ JWT)
    
    Returns:
        ExerciseResponse: Exercise vừa tạo
    
    Raises:
        401 Unauthorized: Nếu chưa login
        422 Validation Error: Nếu dữ liệu không hợp lệ
    
    Example Request Body:
        {
            "description": "Running, custom pace",
            "major_heading": "Running",
            "met_value": 7.5
        }
    """
    exercise = ExerciseService.create_exercise(
        db=db,
        owner_user_id=current_user.id,
        data=data
    )
    
    return ExerciseResponse.model_validate(exercise)


@router.get(
    "/{exercise_id}",
    response_model=ExerciseResponse,
    summary="Get exercise detail",
    description="Lấy chi tiết exercise theo ID."
)
def get_exercise(
    exercise_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> ExerciseResponse:
    """
    GET /exercises/{exercise_id}
    
    Args:
        exercise_id: ID của exercise
        db: Database session
        current_user: User hiện tại
    
    Returns:
        ExerciseResponse: Chi tiết exercise
    
    Raises:
        404 Not Found: Nếu exercise không tồn tại hoặc không có quyền xem
    
    Example:
        GET /exercises/123
    """
    exercise = ExerciseService.get_exercise_by_id(
        db=db,
        exercise_id=exercise_id,
        user_id=current_user.id
    )
    
    return ExerciseResponse.model_validate(exercise)


@router.patch(
    "/{exercise_id}",
    response_model=ExerciseResponse,
    summary="Update custom exercise",
    description="Cập nhật custom exercise. Chỉ owner mới được phép."
)
def update_exercise(
    exercise_id: int,
    data: ExercisePatchRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> ExerciseResponse:
    """
    PATCH /exercises/{exercise_id}
    
    Args:
        exercise_id: ID của exercise
        data: Dữ liệu cần update (partial)
        db: Database session
        current_user: User hiện tại
    
    Returns:
        ExerciseResponse: Exercise sau khi update
    
    Raises:
        403 Forbidden: Nếu không phải owner
        404 Not Found: Nếu exercise không tồn tại
        422 Validation Error: Nếu dữ liệu không hợp lệ
    
    Example Request Body:
        {
            "description": "Updated description",
            "met_value": 8.0
        }
    """
    exercise = ExerciseService.update_exercise(
        db=db,
        exercise_id=exercise_id,
        user_id=current_user.id,
        data=data
    )
    
    return ExerciseResponse.model_validate(exercise)


@router.delete(
    "/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete custom exercise",
    description="Xóa custom exercise (soft delete). Chỉ owner mới được phép."
)
def delete_exercise(
    exercise_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    DELETE /exercises/{exercise_id}
    
    Args:
        exercise_id: ID của exercise cần xóa
        db: Database session
        current_user: User hiện tại
    
    Raises:
        403 Forbidden: Nếu không phải owner
        404 Not Found: Nếu exercise không tồn tại
    
    Example:
        DELETE /exercises/123
    """
    ExerciseService.delete_exercise(
        db=db,
        exercise_id=exercise_id,
        user_id=current_user.id
    )
    # FastAPI tự động trả về 204 No Content