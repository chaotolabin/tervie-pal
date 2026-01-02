"""
Schemas cho Streak API
"""
from datetime import date
from typing import List
from enum import Enum
from pydantic import BaseModel, Field


class StreakStatus(str, Enum):
    """Trạng thái streak hàng ngày"""
    GREEN = "green"    # Hoàn thành đúng hạn
    YELLOW = "yellow"  # Hoàn thành trễ
    NONE = "none"      # Không hoàn thành


class StreakDayResponse(BaseModel):
    """Response cho một ngày trong streak"""
    day: date = Field(..., description="Ngày (YYYY-MM-DD)")
    status: StreakStatus = Field(..., description="Trạng thái: green, yellow, none")

    model_config = {"from_attributes": True}


class StreakResponse(BaseModel):
    """Response cho GET /streak - chuỗi hiện tại + 7 ngày gần nhất"""
    current_streak: int = Field(..., ge=0, description="Chuỗi liên tiếp hiện tại")
    longest_streak: int = Field(..., ge=0, description="Chuỗi dài nhất từ trước đến nay")
    week: List[StreakDayResponse] = Field(..., description="7 ngày gần nhất")

    model_config = {"from_attributes": True}


class StreakWeekResponse(BaseModel):
    """Response cho GET /streak/week - cửa sổ 7 ngày tuỳ chọn"""
    end_day: date = Field(..., description="Ngày cuối cùng của tuần (YYYY-MM-DD)")
    week: List[StreakDayResponse] = Field(..., description="7 ngày từ (end_day-6) đến end_day")

    model_config = {"from_attributes": True}
