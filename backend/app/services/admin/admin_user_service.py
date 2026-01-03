"""
Admin Service - Business Logic cho Admin Panel
Bao gồm: Dashboard Stats, User Management, Blog Management
"""
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from fastapi import HTTPException
import uuid

from app.models.auth import User, Profile, Goal
from app.models.log import FoodLogEntry, ExerciseLogEntry
from app.models.blog import Post
from app.models.streak import UserStreakState
from app.schemas.admin import (
    AdminUserListItem,
    UserActivitySummary,
)


class AdminUserService:
    """Service xử lý User Management"""
    
    @staticmethod
    def get_users_list(
        db: Session,
        page: int = 1,
        page_size: int = 50,
        email_filter: Optional[str] = None,
        role_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> Tuple[List[AdminUserListItem], int]:
        """
        Lấy danh sách users với phân trang và filter
        
        Returns:
            (list_items, total_count)
        """
        query = db.query(
            User,
            Profile.full_name,
            UserStreakState.current_streak
        ).outerjoin(
            Profile, User.id == Profile.user_id
        ).outerjoin(
            UserStreakState, User.id == UserStreakState.user_id
        )
        
        # Filters
        if email_filter:
            query = query.filter(User.email.ilike(f"%{email_filter}%"))
        
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        # Count total
        total = query.count()
        
        # Pagination
        offset = (page - 1) * page_size
        results = query.order_by(desc(User.created_at)).offset(offset).limit(page_size).all()
        
        # Lấy user_ids để query last_log_at (tránh N+1)
        user_ids = [user.id for user, _, _ in results]
        
        # last_log_at = GREATEST(created_at, updated_at)

        # Query last food activity cho tất cả users trong 1 lần
        last_food_map = {}
        if user_ids:
            last_log_food = case(
                (FoodLogEntry.updated_at.is_not(None), FoodLogEntry.updated_at),
                else_=FoodLogEntry.created_at
            )
            food_activities = db.query(
                FoodLogEntry.user_id,
                func.max(last_log_food).label('last_logged')
            ).filter(
                FoodLogEntry.user_id.in_(user_ids),
                FoodLogEntry.deleted_at.is_(None)
            ).group_by(FoodLogEntry.user_id).all()
            
            last_food_map = {user_id: last_logged for user_id, last_logged in food_activities}
        
        # Query last exercise activity cho tất cả users trong 1 lần
        last_exercise_map = {}
        if user_ids:
            last_log_exercise = case(
                (ExerciseLogEntry.updated_at.is_not(None), ExerciseLogEntry.updated_at),
                else_=ExerciseLogEntry.created_at
            )

            exercise_activities = db.query(
                ExerciseLogEntry.user_id,
                func.max(last_log_exercise).label('last_logged')
            ).filter(
                ExerciseLogEntry.user_id.in_(user_ids),
                ExerciseLogEntry.deleted_at.is_(None)
            ).group_by(ExerciseLogEntry.user_id).all()
            
            last_exercise_map = {user_id: last_logged for user_id, last_logged in exercise_activities}
        
        # Build response items
        items = []
        for user, full_name, streak in results:
            last_food = last_food_map.get(user.id)
            last_exercise = last_exercise_map.get(user.id)
            
            last_log = None
            if last_food and last_exercise:
                last_log = max(last_food, last_exercise)
            elif last_food:
                last_log = last_food
            elif last_exercise:
                last_log = last_exercise
            
            items.append(AdminUserListItem(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                full_name=full_name,
                created_at=user.created_at,
                current_streak=streak or 0,
                last_log_at=last_log
            ))
        
        return items, total
    
    @staticmethod
    def get_user_detail(db: Session, user_id: uuid.UUID) -> dict:
        """Lấy chi tiết user kèm activity summary"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        goal = db.query(Goal).filter(Goal.user_id == user_id).first()
        streak_state = db.query(UserStreakState).filter(UserStreakState.user_id == user_id).first()
        
        # Activity summary
        total_food = db.query(func.count(FoodLogEntry.id)).filter(
            FoodLogEntry.user_id == user_id,
            FoodLogEntry.deleted_at.is_(None)
        ).scalar() or 0
        
        total_exercise = db.query(func.count(ExerciseLogEntry.id)).filter(
            ExerciseLogEntry.user_id == user_id,
            ExerciseLogEntry.deleted_at.is_(None)
        ).scalar() or 0
        
        total_posts = db.query(func.count(Post.id)).filter(
            Post.user_id == user_id,
            Post.deleted_at.is_(None)
        ).scalar() or 0
        
        last_food = db.query(func.max(FoodLogEntry.logged_at)).filter(
            FoodLogEntry.user_id == user_id,
            FoodLogEntry.deleted_at.is_(None)
        ).scalar()
        
        last_exercise = db.query(func.max(ExerciseLogEntry.logged_at)).filter(
            ExerciseLogEntry.user_id == user_id,
            ExerciseLogEntry.deleted_at.is_(None)
        ).scalar()
        
        last_post = db.query(func.max(Post.created_at)).filter(
            Post.user_id == user_id,
            Post.deleted_at.is_(None)
        ).scalar()
        
        activity = UserActivitySummary(
            total_food_logs=total_food,
            total_exercise_logs=total_exercise,
            total_posts=total_posts,
            last_food_log_at=last_food,
            last_exercise_log_at=last_exercise,
            last_post_at=last_post
        )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "full_name": profile.full_name if profile else None,
            "gender": profile.gender if profile else None,
            "date_of_birth": profile.date_of_birth if profile else None,
            "height_cm_default": profile.height_cm_default if profile else None,
            "password_changed_at": user.password_changed_at,
            "current_streak": streak_state.current_streak if streak_state else 0,
            "longest_streak": streak_state.longest_streak if streak_state else 0,
            "last_on_time_day": streak_state.last_on_time_day if streak_state else None,
            "activity_summary": activity,
            "goal_type": goal.goal_type if goal else None,
            "daily_calorie_target": goal.daily_calorie_target if goal else None
        }
    
    @staticmethod
    def update_user_role(db: Session, user_id: uuid.UUID, new_role: str, admin_id: uuid.UUID) -> User:
        """Cập nhật role của user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Không cho phép admin tự thay đổi role của chính mình
        if user_id == admin_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot change your own role"
            )
        
        user.role = new_role
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def adjust_user_streak(
        db: Session,
        user_id: uuid.UUID,
        new_streak: int,
        reason: str,
        admin_id: uuid.UUID
    ) -> UserStreakState:
        """Điều chỉnh streak của user (xử lý khiếu nại)"""
        streak_state = db.query(UserStreakState).filter(
            UserStreakState.user_id == user_id
        ).first()
        
        if not streak_state:
            # Tạo mới nếu chưa có
            streak_state = UserStreakState(
                user_id=user_id,
                current_streak=new_streak,
                longest_streak=new_streak,
                updated_at=datetime.now(timezone.utc)
            )
            db.add(streak_state)
        else:
            streak_state.current_streak = new_streak
            if new_streak > streak_state.longest_streak:
                streak_state.longest_streak = new_streak
            streak_state.updated_at = datetime.now(timezone.utc)
        
        # TODO: Log action vào audit table nếu cần
        # AdminAuditLog(admin_id=admin_id, action="adjust_streak", reason=reason, ...)
        
        db.commit()
        db.refresh(streak_state)
        
        return streak_state