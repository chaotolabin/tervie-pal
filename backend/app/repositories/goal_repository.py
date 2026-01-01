# Goal Repository
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.auth import Goal
from decimal import Decimal
import uuid


class GoalRepository:
    """Repository for Goal entity operations"""
    
    @staticmethod
    def create(db: Session, user_id: uuid.UUID, goal_type: str, target_weight_kg: float = None,
               daily_calorie_target: Decimal = None, protein_grams: Decimal = None,
               fat_grams: Decimal = None, carb_grams: Decimal = None,
               weekly_exercise_min: int = None) -> Goal:
        """Create user goal"""
        goal = Goal(
            user_id=user_id,
            goal_type=goal_type,
            target_weight_kg=target_weight_kg,
            daily_calorie_target=daily_calorie_target,
            protein_grams=protein_grams,
            fat_grams=fat_grams,
            carb_grams=carb_grams,
            weekly_exercise_min=weekly_exercise_min or 150
        )
        db.add(goal)
        return goal
