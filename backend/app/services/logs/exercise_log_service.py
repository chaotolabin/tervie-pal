"""
Exercise Log Service - Xử lý nghiệp vụ Exercise Logging
"""
import uuid
from typing import List, Optional
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status

from app.models.log import ExerciseLogEntry, ExerciseLogItem
from app.models.exercise import Exercise
from app.models.biometric import BiometricsLog
from app.schemas.log_schema import (
    ExerciseLogEntryCreate,
    ExerciseLogEntryPatch,
    ExerciseLogItemUpdate
)


class ExerciseLogService:
    """Service xử lý nghiệp vụ Exercise Logging"""

    @staticmethod
    def create_exercise_log(
        db: Session,
        user_id: uuid.UUID,
        data: ExerciseLogEntryCreate
    ) -> ExerciseLogEntry:
        """
        Tạo log buổi tập mới (entry + items)
        
        Business Logic:
        1. Lấy thông tin met_value từ bảng Exercise
        2. Lấy cân nặng hiện tại của user từ BiometricsLog
        3. Tính calories tiêu hao cho từng item
           Formula: Calories = MET × weight(kg) × duration(hours)
        4. Lưu snapshot (met_value_snapshot, calories) vào ExerciseLogItem
        5. Tổng hợp calories tiêu hao
        6. Lưu tổng vào ExerciseLogEntry
        
        Args:
            db: Database session
            user_id: UUID của user
            data: Request data từ client
        
        Returns:
            ExerciseLogEntry: Entry vừa tạo (kèm items)
        
        Raises:
            400: Nếu exercise_id không tồn tại
            422: Nếu không có biometrics log (cân nặng)
        """
        # 1. Lấy cân nặng hiện tại của user
        weight_kg = ExerciseLogService._get_user_weight(db, user_id)
        
        if not weight_kg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot calculate calories: No biometric data found. Please log your weight first."
            )
        
        # 2. Tạo ExerciseLogEntry (chưa có tổng)
        entry = ExerciseLogEntry(
            user_id=user_id,
            logged_at=data.logged_at,
            total_calories=Decimal(0)
        )
        db.add(entry)
        db.flush()  # Để lấy entry.id
        
        # 3. Xử lý từng item và tính calories
        total_calories = Decimal(0)
        
        for item_data in data.items:
            # 3.1. Lấy thông tin exercise
            exercise = db.query(Exercise).filter(
                Exercise.id == item_data.exercise_id,
                Exercise.deleted_at.is_(None)
            ).first()
            
            if not exercise:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Exercise ID {item_data.exercise_id} not found or deleted"
                )
            
            # 3.2. Tính calories tiêu hao
            # Formula: Calories = MET × weight(kg) × duration(hours)
            calories_burned = Decimal(0)
            
            if item_data.duration_min:
                duration_hours = item_data.duration_min / Decimal(60)
                calories_burned = exercise.met_value * Decimal(weight_kg) * duration_hours
                calories_burned = round(calories_burned, 6)
            
            # 3.3. Tạo ExerciseLogItem với snapshot
            log_item = ExerciseLogItem(
                entry_id=entry.id,
                exercise_id=item_data.exercise_id,
                duration_min=item_data.duration_min,
                met_value_snapshot=exercise.met_value,
                calories=calories_burned,
                notes=item_data.notes
            )
            db.add(log_item)
            
            # 3.4. Cộng dồn vào tổng
            total_calories += calories_burned
        
        # 4. Cập nhật tổng vào Entry
        entry.total_calories = round(total_calories, 6)
        
        # 5. Commit transaction
        db.commit()
        db.refresh(entry)
        
        return entry

    @staticmethod
    def _get_user_weight(db: Session, user_id: uuid.UUID) -> Optional[float]:
        """
        Lấy cân nặng mới nhất của user từ BiometricsLog
        
        Returns:
            Optional[float]: Cân nặng (kg) hoặc None nếu chưa có log
        """
        stmt = (
            select(BiometricsLog.weight_kg)
            .where(BiometricsLog.user_id == user_id)
            .order_by(BiometricsLog.logged_at.desc())
            .limit(1)
        )
        
        result = db.execute(stmt)
        weight = result.scalar_one_or_none()
        
        return float(weight) if weight else None

    @staticmethod
    def get_daily_exercise_logs(
        db: Session,
        user_id: uuid.UUID,
        target_date: date
    ) -> List[ExerciseLogEntry]:
        """
        Lấy tất cả buổi tập của user trong 1 ngày
        
        Args:
            db: Database session
            user_id: UUID của user
            target_date: Ngày cần lấy logs
        
        Returns:
            List[ExerciseLogEntry]: Danh sách entries (eager load items)
        """
        # tinh range thoi gian trong ngay (00:00 - 23:59)
        start_dt = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        end_dt = datetime.combine(target_date, datetime.max.time(), tzinfo=timezone.utc)

        stmt = (
            select(ExerciseLogEntry)
            .options(selectinload(ExerciseLogEntry.items))
            .where(
                and_(
                    ExerciseLogEntry.user_id == user_id,
                    ExerciseLogEntry.deleted_at.is_(None),
                    ExerciseLogEntry.logged_at >= start_dt,
                    ExerciseLogEntry.logged_at <= end_dt
                )
            )
            .order_by(ExerciseLogEntry.logged_at.asc())
        )
        
        result = db.execute(stmt)
        entries = result.scalars().all()
        
        return list(entries)

    @staticmethod
    def get_exercise_log_by_id(
        db: Session,
        entry_id: int,
        user_id: uuid.UUID
    ) -> ExerciseLogEntry:
        """
        Lấy chi tiết 1 buổi tập
        
        Args:
            db: Database session
            entry_id: ID của entry
            user_id: UUID của user
        
        Returns:
            ExerciseLogEntry: Entry detail
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
        """
        stmt = (
            select(ExerciseLogEntry)
            .options(selectinload(ExerciseLogEntry.items))
            .where(
                and_(
                    ExerciseLogEntry.id == entry_id,
                    ExerciseLogEntry.user_id == user_id,
                    ExerciseLogEntry.deleted_at.is_(None)
                )
            )
        )
        
        result = db.execute(stmt)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise log entry not found"
            )
        
        return entry

    @staticmethod
    def update_exercise_log(
        db: Session,
        entry_id: int,
        user_id: uuid.UUID,
        data: ExerciseLogEntryPatch
    ) -> ExerciseLogEntry:
        """
        Cập nhật metadata của buổi tập (logged_at)
        
        Note: Không cho phép update items. Nếu muốn thay đổi items,
        phải xóa entry cũ và tạo mới để đảm bảo data consistency.
        
        Args:
            db: Database session
            entry_id: ID của entry
            user_id: UUID của user
            data: Dữ liệu cần update
        
        Returns:
            ExerciseLogEntry: Entry sau khi update
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
        """
        # Get entry (check ownership)
        entry = ExerciseLogService.get_exercise_log_by_id(db, entry_id, user_id)
        
        # Update fields (chỉ update field không None)
        if data.logged_at is not None:
            entry.logged_at = data.logged_at
        
        db.commit()
        db.refresh(entry)
        
        return entry

    @staticmethod
    def update_exercise_log_item(
        db: Session,
        item_id: int,
        user_id: uuid.UUID,
        data: ExerciseLogItemUpdate
    ) -> ExerciseLogItem:
        """
        Cập nhật bài tập trong buổi tập (chỉ duration và notes)
        
        Logic: Sử dụng ratio-based calculation để giữ snapshot consistency.
        Không query lại bảng Exercises.
        
        Formula:
            ratio_calories = old_calories / old_duration_min
            new_calories = ratio_calories * new_duration_min
        
        Args:
            db: Database session
            item_id: ID của item
            user_id: UUID của user
            data: Dữ liệu cần update
        
        Returns:
            ExerciseLogItem: Item sau khi update
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
            400: Nếu dữ liệu không hợp lệ
        """
        # 1. Lấy item và kiểm tra ownership
        stmt = (
            select(ExerciseLogItem)
            .join(ExerciseLogEntry, ExerciseLogEntry.id == ExerciseLogItem.entry_id)
            .where(
                and_(
                    ExerciseLogItem.id == item_id,
                    ExerciseLogEntry.user_id == user_id,
                    ExerciseLogEntry.deleted_at.is_(None)
                )
            )
        )
        
        result = db.execute(stmt)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise log item not found"
            )
        
        # 2. Update notes nếu có
        if data.notes is not None:
            item.notes = data.notes
        
        # 3. Nếu update duration, tính lại calories theo ratio
        if data.duration_min is not None:
            old_duration = item.duration_min
            
            # Handle edge case: old_duration = 0
            if old_duration is None or old_duration == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update item with 0 duration"
                )
            
            new_duration = data.duration_min
            
            # Tính ratio dựa trên dữ liệu cũ
            ratio = new_duration / old_duration
            
            # Update item
            item.duration_min = new_duration
            item.calories = round(item.calories * ratio, 6) if item.calories else None
        
        db.flush()
        
        # 4. Re-aggregate entry totals
        ExerciseLogService._recalculate_entry_totals(db, item.entry_id)
        
        db.commit()
        db.refresh(item)
        
        return item

    @staticmethod
    def _recalculate_entry_totals(db: Session, entry_id: int) -> None:
        """
        Tính lại tổng calories của entry từ tất cả items
        
        Args:
            db: Database session
            entry_id: ID của entry
        """
        # Lấy entry
        entry = db.query(ExerciseLogEntry).filter(ExerciseLogEntry.id == entry_id).first()
        
        if not entry:
            return
        
        # Tính tổng từ tất cả items
        total_calories = Decimal(0)
        
        for item in entry.items:
            total_calories += item.calories or Decimal(0)
        
        # Cập nhật entry
        entry.total_calories = round(total_calories, 6)

    @staticmethod
    def delete_exercise_log(
        db: Session,
        entry_id: int,
        user_id: uuid.UUID
    ) -> None:
        """
        Xóa buổi tập (soft delete)
        
        Args:
            db: Database session
            entry_id: ID của entry
            user_id: UUID của user
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
        """
        # Get entry (check ownership)
        entry = ExerciseLogService.get_exercise_log_by_id(db, entry_id, user_id)
        
        # Soft delete
        entry.deleted_at = datetime.now(timezone.utc)
        
        db.commit()