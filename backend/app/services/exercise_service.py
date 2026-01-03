"""
Service Layer cho Exercise Module
Business logic và CRUD operations cho exercises
"""
import uuid
from typing import List, Tuple, Optional
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.exercise import Exercise
from app.schemas.exercise_schema import ExerciseCreateRequest, ExercisePatchRequest


class ExerciseService:
    """Service xử lý nghiệp vụ Exercise"""

    @staticmethod
    def search_exercises(
        db: Session,
        user_id: uuid.UUID,
        query: str,
        major_heading: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Tuple[List[Exercise], Optional[str]]:
        """
        Tìm kiếm exercises (global + user's custom)
        
        Args:
            db: Database session
            user_id: UUID của user hiện tại
            query: Từ khóa tìm kiếm trong description
            major_heading: Lọc theo nhóm bài tập (optional)
            limit: Số lượng kết quả tối đa
            cursor: ID của exercise cuối cùng ở trang trước
        
        Returns:
            Tuple[List[Exercise], Optional[str]]: 
                - List exercises
                - next_cursor (ID của item cuối cùng, dùng cho trang sau)
        
        Logic:
            - Tìm exercises có description chứa `query` (case-insensitive)
            - Bao gồm: Global exercises (owner_user_id IS NULL) + Custom của user
            - Chưa bị soft delete (deleted_at IS NULL)
            - Phân trang bằng cursor (keyset pagination)
        """
        q = " ".join(query.strip().lower().split())
        tokens = q.split(" ")

        # Base conditions
        conditions = [
            Exercise.deleted_at.is_(None),  # Chưa xóa
            # Exercise.description.ilike(f"%{query}%")  # Tìm kiếm case-insensitive
            
            # Chỉ lấy global exercises + custom của user
            or_(
                Exercise.owner_user_id.is_(None),  # Global
                Exercise.owner_user_id == user_id   # Custom của user
            )
        ]
        
        # token
        tokens_conditions = [
            func.lower(Exercise.description).ilike(f"%{token}%")
            for token in tokens
        ]

        conditions.extend(tokens_conditions)

        # Lọc theo major_heading nếu có
        if major_heading:
            conditions.append(Exercise.major_heading == major_heading)
        
        # Cursor pagination
        if cursor:
            try:
                cursor_id = int(cursor)
                conditions.append(Exercise.id > cursor_id)
            except ValueError:
                # pass  # Invalid cursor, ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid cursor format"
                )
        
        # Build query
        stmt = (
            select(Exercise)
            .where(and_(*conditions))
            .order_by(Exercise.id.asc())
            .limit(limit + 1)  # Lấy thêm 1 để check có trang sau không
        )
        
        result = db.execute(stmt)
        exercises = list(result.scalars().all())
        
        # Xác định next_cursor
        next_cursor = None
        if len(exercises) > limit:
            exercises = exercises[:limit]
            next_cursor = str(exercises[-1].id)
        
        return exercises, next_cursor

    @staticmethod
    def create_exercise(
        db: Session,
        owner_user_id: uuid.UUID,
        data: ExerciseCreateRequest
    ) -> Exercise:
        """
        Tạo custom exercise mới cho user
        
        Args:
            db: Database session
            owner_user_id: UUID của user tạo exercise
            data: Dữ liệu từ request
        
        Returns:
            Exercise: Exercise vừa tạo
        
        Business Rules:
            - Custom exercise luôn có owner_user_id (không phải global)
            - activity_code = None (không phải từ dataset)
            - Validate met_value > 0
        """
        # Validate met_value
        if data.met_value <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="MET value must be greater than 0"
            )
        
        # Tạo exercise mới
        new_exercise = Exercise(
            owner_user_id=owner_user_id,
            activity_code=None,  # Custom exercise không có activity_code
            major_heading=data.major_heading,
            description=data.description,
            met_value=data.met_value,
            deleted_at=None
        )
        
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        
        return new_exercise

    @staticmethod
    def get_exercise_by_id(
        db: Session,
        exercise_id: int,
        user_id: uuid.UUID
    ) -> Exercise:
        """
        Lấy chi tiết exercise theo ID
        
        Args:
            db: Database session
            exercise_id: ID của exercise
            user_id: UUID của user hiện tại
        
        Returns:
            Exercise: Exercise detail
        
        Raises:
            404: Nếu exercise không tồn tại hoặc không có quyền xem
        
        Permission:
            - Global exercise (owner_user_id IS NULL): Ai cũng xem được
            - Custom exercise: Chỉ owner mới xem được
        """
        stmt = select(Exercise).where(
            and_(
                Exercise.id == exercise_id,
                Exercise.deleted_at.is_(None)
            )
        )
        
        result = db.execute(stmt)
        exercise = result.scalar_one_or_none()
        
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        
        # Check permission
        if exercise.owner_user_id is not None and exercise.owner_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"  # Không tiết lộ là do permission
            )
        
        return exercise

    @staticmethod
    def update_exercise(
        db: Session,
        exercise_id: int,
        user_id: uuid.UUID,
        data: ExercisePatchRequest
    ) -> Exercise:
        """
        Cập nhật exercise (chỉ owner hoặc admin)
        
        Args:
            db: Database session
            exercise_id: ID của exercise
            user_id: UUID của user hiện tại
            data: Dữ liệu cần update
        
        Returns:
            Exercise: Exercise sau khi update
        
        Raises:
            403: Nếu không phải owner
            404: Nếu exercise không tồn tại
        
        Business Rules:
            - Chỉ owner mới được update custom exercise
            - Không được update global exercise (owner_user_id IS NULL)
        """
        # Lấy exercise
        exercise = ExerciseService.get_exercise_by_id(db, exercise_id, user_id)
        
        # Check ownership
        if exercise.owner_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update global exercise"
            )
        
        if exercise.owner_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to update this exercise"
            )
        
        # Update fields (chỉ update field không None)
        if data.description is not None:
            exercise.description = data.description
        
        if data.major_heading is not None:
            exercise.major_heading = data.major_heading
        
        if data.met_value is not None:
            if data.met_value <= 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="MET value must be greater than 0"
                )
            exercise.met_value = data.met_value
        
        db.commit()
        db.refresh(exercise)
        
        return exercise

    @staticmethod
    def delete_exercise(
        db: Session,
        exercise_id: int,
        user_id: uuid.UUID
    ) -> None:
        """
        Xóa exercise (soft delete)
        
        Args:
            db: Database session
            exercise_id: ID của exercise
            user_id: UUID của user hiện tại
        
        Raises:
            403: Nếu không phải owner
            404: Nếu exercise không tồn tại
        
        Business Rules:
            - Chỉ owner mới được xóa custom exercise
            - Không được xóa global exercise
            - Soft delete: set deleted_at = now()
        """
        # Lấy exercise
        exercise = ExerciseService.get_exercise_by_id(db, exercise_id, user_id)
        
        # Check ownership
        if exercise.owner_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete global exercise"
            )
        
        if exercise.owner_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to delete this exercise"
            )
        
        # Soft delete
        exercise.deleted_at = datetime.now(timezone.utc)
        
        db.commit()

    @staticmethod
    def calculate_calories_burned(
        met_value: Decimal,
        weight_kg: float,
        duration_minutes: int
    ) -> float:
        """
        Tính calories tiêu hao dựa trên MET
        
        Formula: Calories = MET × weight(kg) × duration(hours)
        
        Args:
            met_value: Giá trị MET của bài tập
            weight_kg: Cân nặng người tập (kg)
            duration_minutes: Thời gian tập (phút)
        
        Returns:
            float: Số calories tiêu hao (làm tròn 1 chữ số)
        
        Example:
            MET = 8.0, weight = 70kg, duration = 30 min
            Calories = 8.0 × 70 × 0.5 = 280 kcal
        """
        if weight_kg <= 0 or duration_minutes <= 0:
            raise ValueError("Weight and duration must be positive")
        
        duration_hours = duration_minutes / 60
        calories = float(met_value) * weight_kg * duration_hours
        
        return round(calories, 1)