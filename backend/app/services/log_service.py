"""
Service Layer cho Food & Exercise Logs
Business logic: Tính toán dinh dưỡng, aggregation, CRUD operations
"""
import uuid
from typing import List, Optional, Tuple
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy import select, and_, func, extract
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status

from app.models.log import (
    FoodLogEntry, FoodLogItem,
    ExerciseLogEntry, ExerciseLogItem,
    MealType
)
from app.models.food import Food, FoodNutrient
from app.models.exercise import Exercise
from app.models.biometric import BiometricsLog
from app.schemas.log_schema import (
    FoodLogEntryCreate,
    FoodLogEntryPatch,
    FoodLogItemCreate,
    FoodLogItemUpdate,
    ExerciseLogEntryCreate,
    ExerciseLogEntryPatch,
    ExerciseLogItemCreate,
    ExerciseLogItemUpdate,
    DailyNutritionSummary
)


# ==================== FOOD LOG SERVICE ====================

class FoodLogService:
    """Service xử lý nghiệp vụ Food Logging"""

    @staticmethod
    def create_food_log(
        db: Session,
        user_id: uuid.UUID,
        data: FoodLogEntryCreate
    ) -> FoodLogEntry:
        """
        Tạo log bữa ăn mới (entry + items)
        
        Business Logic:
        1. Lấy thông tin dinh dưỡng gốc từ bảng Food/FoodNutrient
        2. Tính toán dinh dưỡng cho từng item dựa trên grams người dùng nhập
           Formula: (input_grams / 100) * nutrient_per_100g
        3. Lưu snapshot vào FoodLogItem (calories, protein_g, carbs_g, fat_g)
        4. Tổng hợp (aggregate) dinh dưỡng của tất cả items
        5. Lưu tổng vào FoodLogEntry
        
        Args:
            db: Database session
            user_id: UUID của user
            data: Request data từ client
        
        Returns:
            FoodLogEntry: Entry vừa tạo (kèm items)
        
        Raises:
            400: Nếu food_id không tồn tại
            422: Nếu thiếu thông tin dinh dưỡng
        """
        # 1. Tạo FoodLogEntry (chưa có tổng)
        entry = FoodLogEntry(
            user_id=user_id,
            logged_at=data.logged_at,
            meal_type=data.meal_type,
            total_calories=Decimal(0),
            total_protein_g=Decimal(0),
            total_carbs_g=Decimal(0),
            total_fat_g=Decimal(0)
        )
        db.add(entry)
        db.flush()  # Để lấy entry.id
        
        # 2. Xử lý từng item và tính dinh dưỡng
        total_calories = Decimal(0)
        total_protein = Decimal(0)
        total_carbs = Decimal(0)
        total_fat = Decimal(0)
        
        for item_data in data.items:
            # 2.1. Lấy thông tin food
            food = db.query(Food).filter(
                Food.id == item_data.food_id,
                Food.deleted_at.is_(None)
            ).first()
            
            if not food:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Food ID {item_data.food_id} not found or deleted"
                )
            
            # 2.2. Lấy nutrients của food (calories, protein, carbs, fat)
            nutrients = FoodLogService._get_food_nutrients(db, item_data.food_id)
            
            # 2.3. Tính dinh dưỡng theo grams thực tế
            # Formula: (grams / 100) * amount_per_100g
            multiplier = item_data.grams / Decimal(100)
            
            item_calories = nutrients.get('calories', Decimal(0)) * multiplier
            item_protein = nutrients.get('protein', Decimal(0)) * multiplier
            item_carbs = nutrients.get('carbs', Decimal(0)) * multiplier
            item_fat = nutrients.get('fat', Decimal(0)) * multiplier
            
            # 2.4. Tạo FoodLogItem với snapshot
            log_item = FoodLogItem(
                entry_id=entry.id,
                food_id=item_data.food_id,
                portion_id=item_data.portion_id,
                quantity=item_data.quantity,
                unit=item_data.unit,
                grams=item_data.grams,
                calories=round(item_calories, 6),
                protein_g=round(item_protein, 7),
                carbs_g=round(item_carbs, 7),
                fat_g=round(item_fat, 7)
            )
            db.add(log_item)
            
            # 2.5. Cộng dồn vào tổng
            total_calories += item_calories
            total_protein += item_protein
            total_carbs += item_carbs
            total_fat += item_fat
        
        # 3. Cập nhật tổng vào Entry
        entry.total_calories = round(total_calories, 6)
        entry.total_protein_g = round(total_protein, 7)
        entry.total_carbs_g = round(total_carbs, 7)
        entry.total_fat_g = round(total_fat, 7)
        
        # 4. Commit transaction
        db.commit()
        db.refresh(entry)
        
        return entry

    @staticmethod
    def _get_food_nutrients(db: Session, food_id: int) -> dict:
        """
        Lấy các nutrients quan trọng của food (calories, protein, carbs, fat)
        
        Returns:
            dict: {
                'calories': Decimal,
                'protein': Decimal,
                'carbs': Decimal,
                'fat': Decimal
            }
        """
        nutrients = {}
        
        # Query các nutrients cần thiết
        required_nutrients = ['calories', 'protein', 'carbs', 'fat']
        
        stmt = select(FoodNutrient).where(
            and_(
                FoodNutrient.food_id == food_id,
                FoodNutrient.nutrient_name.in_(required_nutrients)
            )
        )
        
        result = db.execute(stmt)
        nutrient_records = result.scalars().all()
        
        # Map nutrients
        for nutrient in nutrient_records:
            name = nutrient.nutrient_name.lower()
            if name == 'calories':
                nutrients['calories'] = nutrient.amount_per_100g
            elif name == 'protein':
                nutrients['protein'] = nutrient.amount_per_100g
            elif name in ['carbs', 'carbohydrate']:
                nutrients['carbs'] = nutrient.amount_per_100g
            elif name == 'fat':
                nutrients['fat'] = nutrient.amount_per_100g
        
        # Set default 0 nếu thiếu
        nutrients.setdefault('calories', Decimal(0))
        nutrients.setdefault('protein', Decimal(0))
        nutrients.setdefault('carbs', Decimal(0))
        nutrients.setdefault('fat', Decimal(0))
        
        return nutrients

    @staticmethod
    def get_daily_food_logs(
        db: Session,
        user_id: uuid.UUID,
        target_date: date
    ) -> List[FoodLogEntry]:
        """
        Lấy tất cả bữa ăn của user trong 1 ngày
        
        Args:
            db: Database session
            user_id: UUID của user
            target_date: Ngày cần lấy logs (date object)
        
        Returns:
            List[FoodLogEntry]: Danh sách entries (eager load items)
        """
        start_dt = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        end_dt = datetime.combine(target_date, datetime.max.time(), tzinfo=timezone.utc)

        # Sử dụng selectinload để tránh N+1 query
        stmt = (
            select(FoodLogEntry)
            .options(selectinload(FoodLogEntry.items))
            .where(
                and_(
                    FoodLogEntry.user_id == user_id,
                    FoodLogEntry.deleted_at.is_(None),
                    FoodLogEntry.logged_at >= start_dt,
                    FoodLogEntry.logged_at <= end_dt
                )
            )
            .order_by(FoodLogEntry.logged_at.asc())
        )
        
        result = db.execute(stmt)
        entries = result.scalars().all()
        
        return list(entries)

    @staticmethod
    def get_food_log_by_id(
        db: Session,
        entry_id: int,
        user_id: uuid.UUID
    ) -> FoodLogEntry:
        """
        Lấy chi tiết 1 bữa ăn
        
        Args:
            db: Database session
            entry_id: ID của entry
            user_id: UUID của user
        
        Returns:
            FoodLogEntry: Entry detail
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
        """
        stmt = (
            select(FoodLogEntry)
            .options(selectinload(FoodLogEntry.items))
            .where(
                and_(
                    FoodLogEntry.id == entry_id,
                    FoodLogEntry.user_id == user_id,
                    FoodLogEntry.deleted_at.is_(None)
                )
            )
        )
        
        result = db.execute(stmt)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food log entry not found"
            )
        
        return entry

    @staticmethod
    def update_food_log(
        db: Session,
        entry_id: int,
        user_id: uuid.UUID,
        data: FoodLogEntryPatch
    ) -> FoodLogEntry:
        """
        Cập nhật metadata của bữa ăn (logged_at, meal_type)
        
        Note: Không cho phép update items. Nếu muốn thay đổi items,
        phải xóa entry cũ và tạo mới để đảm bảo data consistency.
        
        Args:
            db: Database session
            entry_id: ID của entry
            user_id: UUID của user
            data: Dữ liệu cần update
        
        Returns:
            FoodLogEntry: Entry sau khi update
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
        """
        # Get entry (check ownership)
        entry = FoodLogService.get_food_log_by_id(db, entry_id, user_id)
        
        # Update fields (chỉ update field không None)
        if data.logged_at is not None:
            entry.logged_at = data.logged_at
        
        if data.meal_type is not None:
            entry.meal_type = data.meal_type
        
        db.commit()
        db.refresh(entry)
        
        return entry

    @staticmethod
    def update_food_log_item(
        db: Session,
        item_id: int,
        user_id: uuid.UUID,
        data: FoodLogItemUpdate
    ) -> FoodLogItem:
        """
        Cập nhật món ăn trong bữa ăn (chỉ quantity, unit, grams)
        
        Logic: Sử dụng ratio-based calculation để giữ snapshot consistency.
        Không query lại bảng Foods, chỉ dựa trên dữ liệu hiện có.
        
        Formula:
            ratio_calories = old_calories / old_grams
            new_calories = ratio_calories * new_grams
        
        Args:
            db: Database session
            item_id: ID của item
            user_id: UUID của user
            data: Dữ liệu cần update
        
        Returns:
            FoodLogItem: Item sau khi update
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
            400: Nếu dữ liệu không hợp lệ
        """
        # 1. Lấy item và kiểm tra ownership
        stmt = (
            select(FoodLogItem)
            .join(FoodLogEntry, FoodLogEntry.id == FoodLogItem.entry_id)
            .where(
                and_(
                    FoodLogItem.id == item_id,
                    FoodLogEntry.user_id == user_id,
                    FoodLogEntry.deleted_at.is_(None)
                )
            )
        )
        
        result = db.execute(stmt)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food log item not found"
            )
        
        # 2. Nếu không update grams, chỉ update metadata
        if data.quantity is not None:
            item.quantity = data.quantity
        
        if data.unit is not None:
            item.unit = data.unit
        
        # 3. Nếu update grams, tính lại dinh dưỡng theo ratio
        if data.grams is not None:
            old_grams = item.grams
            
            # Handle edge case: old_grams = 0
            if old_grams == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update item with 0 grams"
                )
            
            new_grams = data.grams
            
            # Tính ratio dựa trên dữ liệu cũ
            ratio = new_grams / old_grams
            
            # Update item
            item.grams = new_grams
            item.calories = round(item.calories * ratio, 6) if item.calories else None
            item.protein_g = round(item.protein_g * ratio, 7) if item.protein_g else None
            item.carbs_g = round(item.carbs_g * ratio, 7) if item.carbs_g else None
            item.fat_g = round(item.fat_g * ratio, 7) if item.fat_g else None
        
        db.flush()
        
        # 4. Re-aggregate entry totals
        FoodLogService._recalculate_entry_totals(db, item.entry_id)
        
        db.commit()
        db.refresh(item)
        
        return item

    @staticmethod
    def _recalculate_entry_totals(db: Session, entry_id: int) -> None:
        """
        Tính lại tổng dinh dưỡng của entry từ tất cả items
        
        Args:
            db: Database session
            entry_id: ID của entry
        """
        # Lấy entry
        entry = db.query(FoodLogEntry).filter(FoodLogEntry.id == entry_id).first()
        
        if not entry:
            return
        
        # Tính tổng từ tất cả items
        total_calories = Decimal(0)
        total_protein = Decimal(0)
        total_carbs = Decimal(0)
        total_fat = Decimal(0)
        
        for item in entry.items:
            total_calories += item.calories or Decimal(0)
            total_protein += item.protein_g or Decimal(0)
            total_carbs += item.carbs_g or Decimal(0)
            total_fat += item.fat_g or Decimal(0)
        
        # Cập nhật entry
        entry.total_calories = round(total_calories, 6)
        entry.total_protein_g = round(total_protein, 7)
        entry.total_carbs_g = round(total_carbs, 7)
        entry.total_fat_g = round(total_fat, 7)

    @staticmethod
    def delete_food_log(
        db: Session,
        entry_id: int,
        user_id: uuid.UUID
    ) -> None:
        """
        Xóa bữa ăn (soft delete)
        
        Args:
            db: Database session
            entry_id: ID của entry
            user_id: UUID của user
        
        Raises:
            404: Nếu không tìm thấy hoặc không có quyền
        """
        # Get entry (check ownership)
        entry = FoodLogService.get_food_log_by_id(db, entry_id, user_id)
        
        # Soft delete
        entry.deleted_at = datetime.now(timezone.utc)
        
        db.commit()


# ==================== EXERCISE LOG SERVICE ====================

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


# ==================== DAILY SUMMARY SERVICE ====================

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