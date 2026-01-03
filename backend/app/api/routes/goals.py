"""
Router cho Goals Module - API Endpoints
Xử lý HTTP requests/responses, gọi Service layer cho business logic

Endpoints:
- GET /goals: Lấy goal hiện tại của user
- PUT /goals: Tạo mới hoặc thay thế toàn bộ goal
- PATCH /goals: Cập nhật một phần goal
- POST /goals/calculate: Tính toán preview (không lưu)
"""
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.services.goal_service import GoalService
from app.schemas.goals import (
    GoalCreateRequest,
    GoalPatchRequest,
    GoalResponse,
    GoalCalculateRequest,
    GoalCalculateResponse,
)


# Tạo router với prefix và tags
router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)


@router.get(
    "",
    response_model=GoalResponse,
    summary="Get current goal",
    description="Lấy goal hiện tại của user. Mỗi user chỉ có 1 goal active."
)
def get_goal(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> GoalResponse:
    """
    GET /goals
    
    Returns:
        GoalResponse: Goal hiện tại của user
    
    Raises:
        404 Not Found: Nếu chưa có goal
    """
    goal = GoalService.get_goal(db, current_user.id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found. Please create a goal first using PUT /goals."
        )
    
    return GoalResponse.model_validate(goal)


@router.put(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or replace goal",
    description="""
    Tạo mới hoặc thay thế toàn bộ goal.
    
    Server sẽ tự động tính:
    - daily_calorie_target: Từ BMR × activity × goal adjustment
    - protein_grams, fat_grams, carb_grams: Từ daily_calorie với tỷ lệ 20/30/50
    
    Yêu cầu:
    - Đã có biometrics log (để lấy weight_kg, height_cm)
    - Đã hoàn thành profile (gender, date_of_birth)
    """
)
def create_or_replace_goal(
    data: GoalCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> GoalResponse:
    """
    PUT /goals - Tạo mới hoặc thay thế goal
    
    Logic:
    1. Lấy latest biometrics → weight_kg, height_cm
    2. Lấy profile → gender, date_of_birth
    3. Tính BMR (Mifflin-St Jeor) → TDEE → daily_calorie → macros
    4. Upsert Goal record
    
    Args:
        data: GoalCreateRequest với goal_type, baseline_activity, etc.
    
    Returns:
        GoalResponse: Goal vừa tạo/cập nhật
    
    Raises:
        400 Bad Request: Nếu thiếu biometrics hoặc profile
    """
    result = GoalService.recalculate_goal(
        db=db,
        user_id=current_user.id,
        goal_type=data.goal_type.value,
        baseline_activity=data.baseline_activity.value,
        weekly_goal=data.weekly_goal,
        target_weight_kg=data.target_weight_kg,
        weekly_exercise_min=data.weekly_exercise_min
    )
    
    return GoalResponse.model_validate(result["goal"])


@router.patch(
    "",
    response_model=GoalResponse,
    summary="Update goal partially",
    description="""
    Cập nhật một phần goal. Chỉ các field được gửi sẽ thay đổi.
    
    Nếu thay đổi goal_type, baseline_activity, hoặc weekly_goal:
    - daily_calorie và macros sẽ được tính lại tự động
    
    Nếu chỉ thay đổi weekly_exercise_min:
    - Không ảnh hưởng đến daily_calorie và macros
    """
)
def update_goal(
    data: GoalPatchRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> GoalResponse:
    """
    PATCH /goals - Cập nhật một phần goal
    
    Args:
        data: GoalPatchRequest với các field optional
    
    Returns:
        GoalResponse: Goal sau khi cập nhật
    
    Raises:
        404 Not Found: Nếu chưa có goal
    """
    # Kiểm tra goal tồn tại
    existing_goal = GoalService.get_goal(db, current_user.id)
    if not existing_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found. Use PUT /goals to create a new goal."
        )
    
    # Nếu chỉ update weekly_exercise_min, không cần recalculate
    update_data = data.model_dump(exclude_unset=True)
    
    if len(update_data) == 1 and "weekly_exercise_min" in update_data:
        goal = GoalService.update_weekly_exercise_min(
            db=db,
            user_id=current_user.id,
            weekly_exercise_min=data.weekly_exercise_min
        )
        return GoalResponse.model_validate(goal)
    
    # Có thay đổi ảnh hưởng đến calculation → recalculate
    result = GoalService.recalculate_goal(
        db=db,
        user_id=current_user.id,
        goal_type=data.goal_type.value if data.goal_type else None,
        baseline_activity=data.baseline_activity.value if data.baseline_activity else None,
        weekly_goal=data.weekly_goal,
        target_weight_kg=data.target_weight_kg,
        weekly_exercise_min=data.weekly_exercise_min
    )
    
    return GoalResponse.model_validate(result["goal"])


@router.post(
    "/calculate",
    response_model=GoalCalculateResponse,
    summary="Calculate goal preview",
    description="""
    Tính toán preview goal KHÔNG lưu vào database.
    
    Hữu ích khi:
    - User muốn xem trước daily_calorie và macros trước khi commit
    - Testing các scenario khác nhau
    """
)
def calculate_goal_preview(
    data: GoalCalculateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> GoalCalculateResponse:
    """
    POST /goals/calculate - Tính preview không lưu
    
    Args:
        data: GoalCalculateRequest với goal_type, baseline_activity, weekly_goal
    
    Returns:
        GoalCalculateResponse: Kết quả tính toán chi tiết
    
    Raises:
        400 Bad Request: Nếu thiếu biometrics hoặc profile
    """
    result = GoalService.calculate_preview(
        db=db,
        user_id=current_user.id,
        goal_type=data.goal_type.value,
        baseline_activity=data.baseline_activity.value,
        weekly_goal=data.weekly_goal or 0.5
    )
    
    return GoalCalculateResponse(**result)
