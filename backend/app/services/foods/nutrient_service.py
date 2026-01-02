"""
Food Nutrients Service
Xử lý CRUD operations cho FoodNutrient
"""
import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.food import FoodNutrient
from app.schemas.food_schema import FoodNutrientCreate
from app.services.foods.permissions import get_food_for_modify, get_food_for_view


class FoodNutrientService:
    """Service xử lý CRUD cho Food Nutrients"""

    @staticmethod
    def create_nutrient(
        db: Session,
        food_id: int,
        user_id: uuid.UUID,
        data: FoodNutrientCreate
    ) -> FoodNutrient:
        """
        Thêm nutrient mới cho food
        
        Args:
            db: Database session
            food_id: ID của food
            user_id: UUID của user
            data: Dữ liệu nutrient
        
        Returns:
            FoodNutrient: Nutrient vừa tạo
        """
        # Kiểm tra quyền (require_owner=True)
        get_food_for_modify(db, food_id, user_id, require_owner=True, load_relationships=False)
        
        # Check duplicate
        existing = db.query(FoodNutrient).filter(
            FoodNutrient.food_id == food_id,
            FoodNutrient.nutrient_name == data.nutrient_name.strip().lower()
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nutrient '{data.nutrient_name}' already exists for this food"
            )
        
        # Tạo nutrient mới
        db_nutrient = FoodNutrient(
            food_id=food_id,
            nutrient_name=data.nutrient_name.strip().lower(),
            unit=data.unit.strip(),
            amount_per_100g=data.amount_per_100g
        )
        db.add(db_nutrient)
        db.commit()
        db.refresh(db_nutrient)
        
        return db_nutrient

    @staticmethod
    def get_nutrients_by_food_id(
        db: Session,
        food_id: int,
        user_id: uuid.UUID
    ) -> List[FoodNutrient]:
        """
        Lấy danh sách nutrients của food
        
        Args:
            db: Database session
            food_id: ID của food
            user_id: UUID của user
        
        Returns:
            List[FoodNutrient]: Danh sách nutrients
        """
        # Kiểm tra quyền xem food (cho phép Global + Custom của user)
        db_food = get_food_for_view(db, food_id, user_id)
        
        return db_food.nutrients

    @staticmethod
    def update_nutrient(
        db: Session,
        food_id: int,
        nutrient_name: str,
        user_id: uuid.UUID,
        data: FoodNutrientCreate
    ) -> FoodNutrient:
        """
        Cập nhật nutrient
        
        Args:
            db: Database session
            food_id: ID của food
            nutrient_name: Tên nutrient cần update
            user_id: UUID của user
            data: Dữ liệu mới
        
        Returns:
            FoodNutrient: Nutrient sau khi update
        """
        # Kiểm tra quyền (require_owner=True)
        get_food_for_modify(db, food_id, user_id, require_owner=True, load_relationships=False)
        
        # Lấy nutrient
        db_nutrient = db.query(FoodNutrient).filter(
            FoodNutrient.food_id == food_id,
            FoodNutrient.nutrient_name == nutrient_name.strip().lower()
        ).first()
        
        if not db_nutrient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrient not found"
            )
        
        # Update (không đổi nutrient_name vì là PK)
        db_nutrient.unit = data.unit.strip()
        db_nutrient.amount_per_100g = data.amount_per_100g
        
        db.commit()
        db.refresh(db_nutrient)
        
        return db_nutrient

    @staticmethod
    def delete_nutrient(
        db: Session,
        food_id: int,
        nutrient_name: str,
        user_id: uuid.UUID
    ) -> None:
        """
        Xóa nutrient
        
        Args:
            db: Database session
            food_id: ID của food
            nutrient_name: Tên nutrient cần xóa
            user_id: UUID của user
        """
        # Kiểm tra quyền (require_owner=True)
        get_food_for_modify(db, food_id, user_id, require_owner=True, load_relationships=False)
        
        # Xóa
        result = db.query(FoodNutrient).filter(
            FoodNutrient.food_id == food_id,
            FoodNutrient.nutrient_name == nutrient_name.strip().lower()
        ).delete()
        
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrient not found"
            )
        
        db.commit()
