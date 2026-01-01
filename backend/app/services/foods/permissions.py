"""
Permissions Module - Base Layer
Xử lý logic kiểm tra quyền truy cập Food
QUAN TRỌNG: File này KHÔNG được import bất kỳ Service nào để tránh circular dependency
"""
import uuid
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status

from app.models.food import Food
from app.models.auth import User, UserRole


def get_food_for_modify(
    db: Session,
    food_id: int,
    user_id: uuid.UUID,
    require_owner: bool = True,
    load_relationships: bool = True
) -> Food:
    """
    Lấy food và kiểm tra quyền truy cập
    
    Logic:
    - Admin: Có thể sửa/xóa tất cả
    - User thường: Chỉ sửa/xóa được custom food của mình
    - Nếu require_owner=False: Chỉ check food tồn tại (dùng cho GET)
    
    Args:
        db: Database session
        food_id: ID của food
        user_id: UUID của user hiện tại
        require_owner: Có yêu cầu phải là owner không (default True)
        load_relationships: Có eager load portions/nutrients không (default True)
    
    Returns:
        Food: Food record nếu có quyền
    
    Raises:
        HTTPException 404: Food không tồn tại
        HTTPException 403: Không có quyền (not owner và không phải admin)
    """
    # Build query
    stmt = select(Food).where(
        and_(
            Food.id == food_id,
            Food.deleted_at.is_(None)
        )
    )
    
    # Eager load relationships nếu cần
    if load_relationships:
        stmt = stmt.options(
            selectinload(Food.portions),
            selectinload(Food.nutrients)
        )
    
    result = db.execute(stmt)
    db_food = result.scalar_one_or_none()
    
    if not db_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    
    # Kiểm tra quyền owner (nếu yêu cầu)
    if require_owner:
        # 1. Lấy user để check role
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # 2. Admin có thể sửa tất cả
        if user.role == UserRole.ADMIN:
            return db_food
        
        # 3. User thường chỉ sửa được của mình
        if db_food.owner_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify your own custom foods"
            )
    
    return db_food


def get_food_for_view(
    db: Session,
    food_id: int,
    user_id: uuid.UUID
) -> Food:
    """
    Kiểm tra quyền XEM food (cho GET endpoints)
    
    Logic:
    - Cho phép xem Global foods (owner_user_id IS NULL)
    - Cho phép xem Custom foods của chính mình
    
    Args:
        db: Database session
        food_id: ID của food
        user_id: UUID của user
    
    Returns:
        Food: Food nếu có quyền xem
    
    Raises:
        HTTPException 404: Food không tồn tại hoặc không có quyền xem
    """    
    stmt = select(Food).where(
        and_(
            Food.id == food_id,
            Food.deleted_at.is_(None),
            or_(
                Food.owner_user_id.is_(None),  # Global
                Food.owner_user_id == user_id  # Custom của user này
            )
        )
    ).options(
        selectinload(Food.portions),
        selectinload(Food.nutrients)
    )
    
    result = db.execute(stmt)
    db_food = result.scalar_one_or_none()
    
    if not db_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found or access denied"
        )
    
    return db_food