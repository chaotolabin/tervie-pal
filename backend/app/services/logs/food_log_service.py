"""
Food Log Service - Xử lý nghiệp vụ Food Logging
"""
import uuid
from typing import List
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status

from app.models.log import FoodLogEntry, FoodLogItem
from app.models.food import Food, FoodNutrient, FoodPortion
from app.schemas.log_schema import (
    FoodLogEntryCreate,
    FoodLogEntryPatch,
    FoodLogItemUpdate,
    FoodLogItemCreateByPortion,
    FoodLogItemCreateByGrams
)


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
            
            # 2.2. Xác định grams và unit dựa trên loại item
            if isinstance(item_data, FoodLogItemCreateByPortion):
                # Loại 1: Dùng portion_id
                portion = db.query(FoodPortion).filter(
                    FoodPortion.id == item_data.portion_id,
                    FoodPortion.food_id == item_data.food_id
                ).first()

                if not portion:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Portion ID {item_data.portion_id} not found or not belong to Food ID {item_data.food_id}"
                    )
                
                grams = portion.grams * item_data.quantity
                unit = portion.unit
                portion_id = item_data.portion_id
                quantity = item_data.quantity
            else:
                # Loại 2: Dùng grams trực tiếp
                grams = item_data.grams
                unit = "g"
                portion_id = None
                quantity = Decimal(1.0)

            # 2.3. Lấy nutrients của food (calories, protein, carbs, fat)
            nutrients = FoodLogService._get_food_nutrients(db, item_data.food_id)
            
            # 2.4. Tính dinh dưỡng theo grams thực tế
            # Formula: (grams / 100) * amount_per_100g
            multiplier = grams / Decimal(100)
            
            item_calories = nutrients.get('calories', Decimal(0)) * multiplier
            item_protein = nutrients.get('protein', Decimal(0)) * multiplier
            item_carbs = nutrients.get('carbs', Decimal(0)) * multiplier
            item_fat = nutrients.get('fat', Decimal(0)) * multiplier
            
            # 2.5. Tạo FoodLogItem với snapshot
            log_item = FoodLogItem(
                entry_id=entry.id,
                food_id=item_data.food_id,
                portion_id=portion_id,
                quantity=quantity,
                unit=unit,
                grams=grams,
                calories=round(item_calories, 6),
                protein_g=round(item_protein, 7),
                carbs_g=round(item_carbs, 7),
                fat_g=round(item_fat, 7)
            )
            db.add(log_item)
            
            # 2.6. Cộng dồn vào tổng
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