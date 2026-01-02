"""
Router cho Streak Module - API Endpoints
Xử lý HTTP requests/responses, gọi Service layer cho business logic
"""
from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.services.streak_service import StreakService
from app.schemas.streak import (
    StreakResponse,
    StreakWeekResponse
)


# Tạo router với prefix và tags
router = APIRouter(
    prefix="/streak",
    tags=["Streak"]
)


@router.get(
    "",
    response_model=StreakResponse,
    summary="Get current streak + last 7 days",
    description="Lấy chuỗi hiện tại, chuỗi dài nhất, và trạng thái 7 ngày gần nhất"
)
def get_streak(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> StreakResponse:
    """
    GET /streak
    
    Returns:
        StreakResponse: 
            - current_streak: Chuỗi liên tiếp hiện tại (số ngày)
            - longest_streak: Chuỗi dài nhất từ trước đến nay
            - week: 7 ngày gần nhất với status của mỗi ngày
    
    Example response:
        {
            "current_streak": 5,
            "longest_streak": 12,
            "week": [
                {"day": "2025-12-26", "status": "green"},
                {"day": "2025-12-27", "status": "green"},
                ...
                {"day": "2026-01-01", "status": "yellow"}
            ]
        }
    """
    return StreakService.get_streak(db, current_user.id)


@router.get(
    "/week",
    response_model=StreakWeekResponse,
    summary="Get a 7-day streak window",
    description="Lấy trạng thái streak cho 7 ngày tùy chọn (end_day là ngày cuối)"
)
def get_streak_week(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    end_day: Annotated[Optional[date], Query(
        alias="end_day",
        description="Ngày cuối cùng của tuần (YYYY-MM-DD). Mặc định là hôm nay"
    )] = None
) -> StreakWeekResponse:
    """
    GET /streak/week?end_day=2026-01-02
    
    Lấy cửa sổ 7 ngày từ (end_day - 6) đến end_day
    
    Args:
        end_day: Ngày cuối cùng (optional, default = hôm nay)
    
    Returns:
        StreakWeekResponse:
            - end_day: Ngày cuối cùng của cửa sổ
            - week: 7 ngày với status
    
    Example:
        GET /streak/week  # 7 ngày gần nhất
        GET /streak/week?end_day=2025-12-25  # 7 ngày kết thúc 25-12
    """
    return StreakService.get_streak_week(db, current_user.id, end_day)
