"""
API Routes cho Daily Logs (Food & Exercise tracking)
Endpoints: POST/GET/DELETE food logs và exercise logs
"""
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.auth import User
from app.schemas.log_schema import (
    # Food Log
    FoodLogEntryCreate,
    FoodLogEntryResponse,
    FoodLogEntryPatch,
    FoodLogItemResponse,
    FoodLogItemUpdate,
    # Exercise Log
    ExerciseLogEntryCreate,
    ExerciseLogEntryResponse,
    ExerciseLogEntryPatch,
    ExerciseLogItemResponse,
    ExerciseLogItemUpdate,
    # Daily Summary
    DailyLogsResponse,
    DailyNutritionSummary
)
from app.services.logs import (
    FoodLogService, 
    ExerciseLogService,
    DailyLogService
)

router = APIRouter(tags=["Logs"])

# ==================== FOOD LOG ENDPOINTS ====================

@router.post(
    "/food",
    response_model=FoodLogEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo log bữa ăn mới",
    description="""
    Tạo log bữa ăn mới với danh sách món ăn.
    
    **2 Cách nhập món ăn:**
    1. **Sử dụng portion có sẵn:**
       - Gửi `food_id`, `portion_id`, `quantity`
       - Server tự tính: `grams = quantity × portion.grams`
       - Server tự set `unit = portion.unit`
    
    2. **Nhập grams trực tiếp:**
       - Gửi `food_id`, `grams`
       - Server set `unit = "g"`, `portion_id = null`
    
    **Business Logic:**
    - Server tự động tính toán dinh dưỡng (calories, protein, carbs, fat) dựa trên grams
    - Lưu snapshot để giữ nguyên lịch sử dù food gốc có thay đổi
    - Tổng hợp dinh dưỡng của tất cả items vào entry
    
    **Validation:**
    - Bữa ăn phải có ít nhất 1 món
    - Food ID phải tồn tại và chưa bị xóa
    - Nếu dùng portion: Portion ID phải tồn tại và thuộc đúng food_id
    - Quantity/Grams phải > 0
    """
)
def create_food_log(
    data: FoodLogEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo log bữa ăn mới"""
    entry = FoodLogService.create_food_log(db, current_user.id, data)
    return entry


@router.get(
    "/food/daily/{target_date}",
    response_model=List[FoodLogEntryResponse],
    summary="Lấy tất cả bữa ăn trong ngày",
    description="""
    Lấy danh sách tất cả bữa ăn của user trong 1 ngày cụ thể.
    
    **Response:**
    - Danh sách entries (kèm theo items chi tiết)
    - Sắp xếp theo thời gian tăng dần
    - Chỉ lấy entries chưa bị xóa (deleted_at IS NULL)
    """
)
def get_daily_food_logs(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy tất cả bữa ăn trong ngày"""
    entries = FoodLogService.get_daily_food_logs(db, current_user.id, target_date)
    return entries


@router.get(
    "/food/{entry_id}",
    response_model=FoodLogEntryResponse,
    summary="Lấy chi tiết 1 bữa ăn",
    description="Lấy thông tin chi tiết của 1 bữa ăn (kèm items)"
)
def get_food_log_detail(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy chi tiết 1 bữa ăn"""
    entry = FoodLogService.get_food_log_by_id(db, entry_id, current_user.id)
    return entry


@router.patch(
    "/food/{entry_id}",
    response_model=FoodLogEntryResponse,
    summary="Cập nhật bữa ăn",
    description="""
    Cập nhật metadata của bữa ăn (logged_at, meal_type).
    
    **Giới hạn:**
    - Chỉ có thể update logged_at và meal_type
    - Không thể thay đổi items (món ăn)
    - Nếu muốn thay đổi items, phải xóa và tạo mới
    
    **Logic:**
    - Chỉ owner mới được update
    - Chỉ update các field không null trong request
    """
)
def update_food_log(
    entry_id: int,
    data: FoodLogEntryPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật bữa ăn"""
    entry = FoodLogService.update_food_log(db, entry_id, current_user.id, data)
    return entry


@router.patch(
    "/food/items/{item_id}",
    response_model=FoodLogItemResponse,
    summary="Cập nhật món ăn",
    description="""
    Cập nhật chi tiết món ăn trong bữa ăn.
    
    **Logic:**
    - Sử dụng ratio-based calculation để giữ snapshot consistency
    - Không query lại bảng Foods, chỉ dựa trên dữ liệu hiện có
    - Tự động tính lại tổng dinh dưỡng của entry
    
    **Công thức:**
    - ratio = new_grams / old_grams
    - new_calories = old_calories * ratio
    
    **Validation:**
    - Chỉ owner mới được update
    - Không thể update item có grams = 0
    """
)
def update_food_log_item(
    item_id: int,
    data: FoodLogItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật món ăn trong bữa ăn"""
    item = FoodLogService.update_food_log_item(db, item_id, current_user.id, data)
    return item


@router.delete(
    "/food/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa bữa ăn",
    description="""
    Xóa bữa ăn (soft delete).
    
    **Logic:**
    - Chỉ xóa mềm (set deleted_at = now())
    - Không xóa vật lý để giữ lại lịch sử
    - Chỉ owner mới được xóa
    """
)
def delete_food_log(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xóa bữa ăn (soft delete)"""
    FoodLogService.delete_food_log(db, entry_id, current_user.id)
    return None


# ==================== EXERCISE LOG ENDPOINTS ====================

@router.post(
    "/exercise",
    response_model=ExerciseLogEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo log buổi tập mới",
    description="""
    Tạo log buổi tập mới với danh sách bài tập.
    
    **Business Logic:**
    - Server tự động tính calories tiêu hao dựa trên:
        * MET value của bài tập
        * Cân nặng hiện tại của user (từ biometrics_logs)
        * Thời gian tập (duration_min)
    - Formula: Calories = MET × weight(kg) × duration(hours)
    - Lưu snapshot (met_value, calories) để giữ nguyên lịch sử
    
    **Validation:**
    - Buổi tập phải có ít nhất 1 bài tập
    - Exercise ID phải tồn tại và chưa bị xóa
    - Duration phải > 0
    - User phải có ít nhất 1 biometric log (để lấy cân nặng)
    """
)
def create_exercise_log(
    data: ExerciseLogEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo log buổi tập mới"""
    entry = ExerciseLogService.create_exercise_log(db, current_user.id, data)
    return entry


@router.get(
    "/exercise/daily/{target_date}",
    response_model=List[ExerciseLogEntryResponse],
    summary="Lấy tất cả buổi tập trong ngày",
    description="""
    Lấy danh sách tất cả buổi tập của user trong 1 ngày cụ thể.
    
    **Response:**
    - Danh sách entries (kèm theo items chi tiết)
    - Sắp xếp theo thời gian tăng dần
    - Chỉ lấy entries chưa bị xóa
    """
)
def get_daily_exercise_logs(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy tất cả buổi tập trong ngày"""
    entries = ExerciseLogService.get_daily_exercise_logs(db, current_user.id, target_date)
    return entries


@router.get(
    "/exercise/{entry_id}",
    response_model=ExerciseLogEntryResponse,
    summary="Lấy chi tiết 1 buổi tập",
    description="Lấy thông tin chi tiết của 1 buổi tập (kèm items)"
)
def get_exercise_log_detail(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy chi tiết 1 buổi tập"""
    entry = ExerciseLogService.get_exercise_log_by_id(db, entry_id, current_user.id)
    return entry


@router.patch(
    "/exercise/{entry_id}",
    response_model=ExerciseLogEntryResponse,
    summary="Cập nhật buổi tập",
    description="""
    Cập nhật metadata của buổi tập (logged_at).
    
    **Giới hạn:**
    - Chỉ có thể update logged_at
    - Không thể thay đổi items (bài tập)
    - Nếu muốn thay đổi items, phải xóa và tạo mới
    
    **Logic:**
    - Chỉ owner mới được update
    - Chỉ update các field không null trong request
    """
)
def update_exercise_log(
    entry_id: int,
    data: ExerciseLogEntryPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật buổi tập"""
    entry = ExerciseLogService.update_exercise_log(db, entry_id, current_user.id, data)
    return entry


@router.patch(
    "/exercise/items/{item_id}",
    response_model=ExerciseLogItemResponse,
    summary="Cập nhật bài tập",
    description="""
    Cập nhật chi tiết bài tập trong buổi tập.
    
    **Logic:**
    - Sử dụng ratio-based calculation để giữ snapshot consistency
    - Không query lại bảng Exercises, chỉ dựa trên dữ liệu hiện có
    - Tự động tính lại tổng calories của entry
    
    **Công thức:**
    - ratio = new_duration / old_duration
    - new_calories = old_calories * ratio
    
    **Validation:**
    - Chỉ owner mới được update
    - Không thể update item có duration = 0
    """
)
def update_exercise_log_item(
    item_id: int,
    data: ExerciseLogItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật bài tập trong buổi tập"""
    item = ExerciseLogService.update_exercise_log_item(db, item_id, current_user.id, data)
    return item


@router.delete(
    "/exercise/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa buổi tập",
    description="""
    Xóa buổi tập (soft delete).
    
    **Logic:**
    - Chỉ xóa mềm (set deleted_at = now())
    - Chỉ owner mới được xóa
    """
)
def delete_exercise_log(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xóa buổi tập (soft delete)"""
    ExerciseLogService.delete_exercise_log(db, entry_id, current_user.id)
    return None


# ==================== DAILY SUMMARY ENDPOINT ====================

@router.get(
    "/daily/{target_date}",
    response_model=DailyLogsResponse,
    summary="Lấy tất cả logs và tổng kết trong ngày",
    description="""
    Lấy tất cả logs (food + exercise) và tổng kết dinh dưỡng trong 1 ngày.
    
    **Response:**
    - Danh sách tất cả food logs
    - Danh sách tất cả exercise logs
    - Summary:
        * Tổng calories ăn vào
        * Tổng calories tiêu hao
        * Net calories (ăn vào - tiêu hao)
        * Tổng protein, carbs, fat
    """
)
def get_daily_logs_summary(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy tất cả logs và tổng kết trong ngày"""
    # Lấy food logs
    food_logs = FoodLogService.get_daily_food_logs(db, current_user.id, target_date)
    
    # Lấy exercise logs
    exercise_logs = ExerciseLogService.get_daily_exercise_logs(db, current_user.id, target_date)
    
    # Tính summary
    summary = DailyLogService.get_daily_summary(db, current_user.id, target_date)
    
    return DailyLogsResponse(
        date=target_date.isoformat(),
        food_logs=food_logs,
        exercise_logs=exercise_logs,
        summary=summary
    )


@router.get(
    "/summary/{target_date}",
    response_model=DailyNutritionSummary,
    summary="Lấy tổng kết dinh dưỡng trong ngày",
    description="""
    Lấy chỉ số tổng kết dinh dưỡng trong 1 ngày (không bao gồm chi tiết logs).
    
    **Use case:** Hiển thị dashboard, charts, progress tracking
    """
)
def get_daily_nutrition_summary(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy tổng kết dinh dưỡng trong ngày"""
    summary = DailyLogService.get_daily_summary(db, current_user.id, target_date)
    return summary