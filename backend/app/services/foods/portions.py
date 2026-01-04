"""
Food Portions Service
Xử lý CRUD operations cho FoodPortion
"""
import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.food import FoodPortion
from app.schemas.food_schema import FoodPortionCreate
from app.services.foods.permissions import get_food_for_modify, get_food_for_view


class FoodPortionService:
    """Service xử lý CRUD cho Food Portions"""

    @staticmethod
    def create_portion(
        db: Session,
        food_id: int,
        user_id: uuid.UUID,
        data: FoodPortionCreate
    ) -> FoodPortion:
        """
        Thêm portion mới cho food
        
        Args:
            db: Database session
            food_id: ID của food
            user_id: UUID của user (để check permission)
            data: Dữ liệu portion
        
        Returns:
            FoodPortion: Portion vừa tạo
        """
        # Kiểm tra food tồn tại và có quyền (require_owner=True)
        get_food_for_modify(db, food_id, user_id, require_owner=True, load_relationships=False)
        
        # Tạo portion mới
        db_portion = FoodPortion(
            food_id=food_id,
            amount=data.amount,
            unit=data.unit.strip(),
            grams=data.grams
        )
        db.add(db_portion)
        db.commit()
        db.refresh(db_portion)
        
        return db_portion

    @staticmethod
    def get_portions_by_food_id(
        db: Session,
        food_id: int,
        user_id: uuid.UUID
    ) -> List[FoodPortion]:
        """
        Lấy danh sách portions của food
        
        Args:
            db: Database session
            food_id: ID của food
            user_id: UUID của user
        
        Returns:
            List[FoodPortion]: Danh sách portions
        """
        # Kiểm tra quyền xem food (cho phép Global + Custom của user)
        db_food = get_food_for_view(db, food_id, user_id)
        
        return db_food.portions

    @staticmethod
    def update_portion(
        db: Session,
        food_id: int,
        portion_id: int,
        user_id: uuid.UUID,
        data: FoodPortionCreate
    ) -> FoodPortion:
        """
        Cập nhật portion
        
        Args:
            db: Database session
            food_id: ID của food
            portion_id: ID của portion
            user_id: UUID của user
            data: Dữ liệu mới
        
        Returns:
            FoodPortion: Portion sau khi update
        """
        # Kiểm tra quyền (require_owner=True)
        get_food_for_modify(db, food_id, user_id, require_owner=True, load_relationships=False)
        
        # Lấy portion
        db_portion = db.query(FoodPortion).filter(
            FoodPortion.id == portion_id,
            FoodPortion.food_id == food_id
        ).first()
        
        if not db_portion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portion not found"
            )
        
        # Update
        db_portion.amount = data.amount
        db_portion.unit = data.unit.strip()
        db_portion.grams = data.grams
        
        db.commit()
        db.refresh(db_portion)
        
        return db_portion

    @staticmethod
    def delete_portion(
        db: Session,
        food_id: int,
        portion_id: int,
        user_id: uuid.UUID
    ) -> None:
        """
        Xóa portion
        
        Args:
            db: Database session
            food_id: ID của food
            portion_id: ID của portion
            user_id: UUID của user
        """
        # Kiểm tra quyền (require_owner=True)
        get_food_for_modify(db, food_id, user_id, require_owner=True, load_relationships=False)
        
        # Xóa
        result = db.query(FoodPortion).filter(
            FoodPortion.id == portion_id,
            FoodPortion.food_id == food_id
        ).delete()
        
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portion not found"
            )
        
        db.commit()