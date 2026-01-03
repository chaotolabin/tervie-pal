"""
Food Core Service
Xử lý CRUD operations chính cho Food (Search, Create, Get, Update, Delete)
"""
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.food import Food, FoodPortion, FoodNutrient
from app.schemas.food import (
    FoodCreateRequest,
    FoodPatchRequest
)
from app.services.foods.permissions import get_food_for_modify, get_food_for_view


class FoodService:
    """Service xử lý nghiệp vụ Foods chính"""

    @staticmethod
    def search_foods(
        db: Session,
        user_id: uuid.UUID,
        query: str,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Tuple[List[Food], Optional[str]]:
        """
        Tìm kiếm foods theo tên
        
        Logic:
        - Tìm các food có tên chứa `query` (case-insensitive)
        - Phạm vi: Global foods (owner_user_id IS NULL) + Custom foods của user
        - Loại bỏ các food đã bị soft delete
        - Cursor-based pagination (dùng food.id)
        
        Args:
            db: Database session
            user_id: UUID của user hiện tại
            query: Từ khóa tìm kiếm
            limit: Số lượng kết quả tối đa (1-100)
            cursor: ID của food cuối cùng trong trang trước (dùng cho pagination)
        
        Returns:
            Tuple[List[Food], Optional[str]]: (Danh sách foods, next_cursor)
        """
        # Build query: tìm global + custom của user
        q = " ".join(query.strip().lower().split())
        tokens = q.split(" ")

        conditions = [
            func.lower(Food.name).ilike(f"%{token}%")
            for token in tokens
        ]

        stmt = select(Food).where(
            and_(
                Food.deleted_at.is_(None),  # Chưa bị xóa
                or_(
                    Food.owner_user_id.is_(None),   # Global food
                    Food.owner_user_id == user_id   # Custom của user này
                ),
                *conditions   # tất cả token đều phải match
            )
        )
        
        # Cursor pagination: nếu có cursor, chỉ lấy foods có id > cursor
        if cursor:
            try:
                cursor_id = int(cursor)
                stmt = stmt.where(Food.id > cursor_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid cursor format"
                )
        
        # Sắp xếp theo id tăng dần và limit
        stmt = stmt.order_by(Food.id.asc()).limit(limit + 1)  # Lấy thêm 1 để check có trang sau không
        
        result = db.execute(stmt)
        foods = list(result.scalars().all())
        
        # Xác định next_cursor
        next_cursor = None
        if len(foods) > limit:
            # Có trang tiếp theo
            foods = foods[:limit]  # Bỏ item thừa
            next_cursor = str(foods[-1].id)  # Cursor là id của item cuối
        
        return foods, next_cursor

    @staticmethod
    def create_food(
        db: Session,
        user_id: uuid.UUID,
        data: FoodCreateRequest
    ) -> Food:
        """
        Tạo custom food mới (owner = user_id)
        
        Logic:
        - Tạo Food record với owner_user_id = user_id
        - Tạo các FoodPortion records (nếu có)
        - Tạo các FoodNutrient records (bắt buộc)
        - Sử dụng transaction để đảm bảo tính toàn vẹn
        
        Args:
            db: Database session
            user_id: UUID của user tạo food
            data: Dữ liệu từ request
        
        Returns:
            Food: Food vừa tạo (bao gồm portions và nutrients)
        
        Raises:
            HTTPException 400: Nếu có lỗi logic (duplicate, invalid data...)
        """
        try:
            # 1. Tạo Food record
            db_food = Food(
                owner_user_id=user_id,  # Custom food của user
                source_code=data.source_code,
                name=data.name.strip(),
                food_group=data.food_group.strip() if data.food_group else None
            )
            db.add(db_food)
            db.flush()  # Flush để có food.id cho FK
            
            # 2. Tạo FoodPortion records
            for portion_data in data.portions:
                db_portion = FoodPortion(
                    food_id=db_food.id,
                    amount=portion_data.amount,
                    unit=portion_data.unit.strip(),
                    grams=portion_data.grams
                )
                db.add(db_portion)
            
            # 3. Tạo FoodNutrient records
            for nutrient_data in data.nutrients:
                db_nutrient = FoodNutrient(
                    food_id=db_food.id,
                    nutrient_name=nutrient_data.nutrient_name.strip().lower(),
                    unit=nutrient_data.unit.strip(),
                    amount_per_100g=nutrient_data.amount_per_100g
                )
                db.add(db_nutrient)
            
            # Commit transaction
            db.commit()
            
            # Refresh để load relationships
            db.refresh(db_food)
            
            return db_food

        except IntegrityError as ie:
            db.rollback()
            # Kiểm tra lỗi duplicate (ví dụ source_code đã tồn tại)
            if 'uq_foods_source_code_global' in str(ie.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Food with this source_code already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Database integrity error"
                ) 
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create food: {str(e)}"
            )

    @staticmethod
    def get_food_by_id(
        db: Session,
        food_id: int,
        user_id: uuid.UUID
    ) -> Food:
        """
        Lấy food detail theo ID
        
        Logic:
        - Chỉ trả về food nếu: Global HOẶC owner = user_id
        - Load sẵn portions và nutrients (eager loading)
        - Không trả về food đã bị soft delete
        
        Args:
            db: Database session
            food_id: ID của food
            user_id: UUID của user hiện tại
        
        Returns:
            Food: Food detail
        
        Raises:
            HTTPException 404: Nếu không tìm thấy food hoặc không có quyền xem
        """
        return get_food_for_view(db, food_id, user_id)

    @staticmethod
    def update_food(
        db: Session,
        food_id: int,
        user_id: uuid.UUID,
        data: FoodPatchRequest
    ) -> Food:
        """
        Cập nhật food metadata (chỉ name và food_group)
        
        Logic:
        - Kiểm tra quyền (owner hoặc admin)
        - Chỉ update các trường cơ bản: name, food_group
        - Để update portions/nutrients, dùng FoodPortionService và FoodNutrientService
        
        Args:
            db: Database session
            food_id: ID của food cần update
            user_id: UUID của user hiện tại
            data: Dữ liệu update (chỉ name, food_group)
        
        Returns:
            Food: Food sau khi update
        
        Raises:
            HTTPException 403: Không có quyền
            HTTPException 404: Food không tồn tại
        """
        # Kiểm tra quyền (require_owner=True)
        db_food = get_food_for_modify(db, food_id, user_id, require_owner=True)
        
        try:
            # Update các trường cơ bản
            if data.name is not None:
                db_food.name = data.name.strip()
            
            if data.food_group is not None:
                db_food.food_group = data.food_group.strip() if data.food_group else None
            
            # Commit
            db.commit()
            db.refresh(db_food)
            
            return db_food
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update food: {str(e)}"
            )

    @staticmethod
    def delete_food(
        db: Session,
        food_id: int,
        user_id: uuid.UUID
    ) -> None:
        """
        Xóa food (soft delete)
        
        Logic:
        - Kiểm tra quyền (owner hoặc admin)
        - Set deleted_at = now()
        - Không xóa thật để giữ lại history
        
        Args:
            db: Database session
            food_id: ID của food cần xóa
            user_id: UUID của user hiện tại
        
        Raises:
            HTTPException 403: Không có quyền
            HTTPException 404: Food không tồn tại
        """
        # Kiểm tra quyền (require_owner=True)
        db_food = get_food_for_modify(db, food_id, user_id, require_owner=True, load_relationships=False)
        
        # Soft delete
        db_food.deleted_at = datetime.now(timezone.utc)
        
        db.commit()