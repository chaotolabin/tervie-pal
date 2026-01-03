"""
Daily Log Service - Xử lý tổng hợp logs hàng ngày
"""
import uuid
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.schemas.log import DailyNutritionSummary
from app.services.logs.food_log_service import FoodLogService
from app.services.logs.exercise_log_service import ExerciseLogService


class DailyLogService:
    """Service xử lý tổng hợp logs hàng ngày"""

    @staticmethod
    def get_daily_summary(
        db: Session,
        user_id: uuid.UUID,
        target_date: date
    ) -> DailyNutritionSummary:
        """
        Tính tổng hợp dinh dưỡng trong 1 ngày
        
        Args:
            db: Database session
            user_id: UUID của user
            target_date: Ngày cần tổng hợp
        
        Returns:
            DailyNutritionSummary: Tổng kết calories và macros
        """
        # Lấy food logs
        food_logs = FoodLogService.get_daily_food_logs(db, user_id, target_date)
        
        # Lấy exercise logs
        exercise_logs = ExerciseLogService.get_daily_exercise_logs(db, user_id, target_date)
        
        # Tính tổng
        total_calories_consumed = sum(
            (entry.total_calories for entry in food_logs),
            start=Decimal(0)
        )
        
        total_calories_burned = sum(
            (entry.total_calories for entry in exercise_logs),
            start=Decimal(0)
        )
        
        total_protein = sum(
            (entry.total_protein_g for entry in food_logs),
            start=Decimal(0)
        )
        
        total_carbs = sum(
            (entry.total_carbs_g for entry in food_logs),
            start=Decimal(0)
        )
        
        total_fat = sum(
            (entry.total_fat_g for entry in food_logs),
            start=Decimal(0)
        )
        
        net_calories = total_calories_consumed - total_calories_burned
        
        return DailyNutritionSummary(
            date=target_date.isoformat(),
            total_calories_consumed=round(total_calories_consumed, 6),
            total_calories_burned=round(total_calories_burned, 6),
            net_calories=round(net_calories, 6),
            total_protein_g=round(total_protein, 7),
            total_carbs_g=round(total_carbs, 7),
            total_fat_g=round(total_fat, 7)
        )