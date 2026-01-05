"""
API Routes cho Admin Contributions Management
Endpoints: GET/POST/DELETE /admin/contributions/{type}
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_, or_

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.auth import User
from app.models.food import Food
from app.models.exercise import Exercise
from app.models.notification import Notification
from app.schemas.food import FoodDetail
from app.schemas.exercise import ExerciseResponse


router = APIRouter()


# ==================== CONTRIBUTIONS ENDPOINTS ====================

@router.get(
    "/contributions/foods",
    response_model=List[FoodDetail],
    summary="Admin - Get Pending Food Contributions",
    description="""
    Lấy danh sách các đóng góp thực phẩm đang chờ duyệt.
    
    **Authorization:** Chỉ admin
    
    **Filtering:**
    - status: pending (mặc định), approved, rejected
    
    **Returns:**
    - Danh sách foods với is_contribution=true và contribution_status=pending
    - Bao gồm thông tin creator (username, email)
    """
)
def get_pending_food_contributions(
    status: str = Query("pending", description="Filter theo status: pending, approved, rejected"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
) -> List[FoodDetail]:
    """Lấy danh sách pending food contributions"""
    
    # Normalize status để tránh case sensitivity issues
    status = status.lower().strip()
    
    # Debug: Kiểm tra tổng số foods với is_contribution=True
    total_contributions = db.query(Food).filter(
        Food.is_contribution == True,
        Food.deleted_at.is_(None)
    ).count()
    print(f"[DEBUG] Total foods with is_contribution=True: {total_contributions}")
    
    # Debug: Kiểm tra foods với status cụ thể
    pending_count = db.query(Food).filter(
        Food.is_contribution == True,
        Food.contribution_status == status,
        Food.deleted_at.is_(None)
    ).count()
    print(f"[DEBUG] Foods with is_contribution=True AND contribution_status='{status}': {pending_count}")
    
    # Debug: List một vài foods với is_contribution=True để xem status của chúng
    sample_foods = db.query(Food.id, Food.name, Food.is_contribution, Food.contribution_status, Food.owner_user_id).filter(
        Food.is_contribution == True,
        Food.deleted_at.is_(None)
    ).limit(5).all()
    print(f"[DEBUG] Sample foods with is_contribution=True:")
    for f in sample_foods:
        print(f"  - ID: {f.id}, Name: {f.name}, Status: {f.contribution_status}, Owner: {f.owner_user_id}")
    
    # Query foods với is_contribution=True và status phù hợp
    # Nếu status là 'pending', cũng bao gồm các record có contribution_status IS NULL
    # (để xử lý các record cũ được tạo trước khi có logic contribution_status)
    if status == 'pending':
        status_filter = or_(
            Food.contribution_status == status,
            Food.contribution_status.is_(None)
        )
    else:
        status_filter = Food.contribution_status == status
    
    # Eager load portions và nutrients để tránh N+1 queries
    # Query Food objects first, then get User info separately to avoid Row tuple issues
    stmt = (
        select(Food)
        .options(
            selectinload(Food.portions),
            selectinload(Food.nutrients)
        )
        .where(
            and_(
                Food.is_contribution == True,
                status_filter,
                Food.deleted_at.is_(None)
            )
        )
        .order_by(Food.created_at.desc())
    )
    
    foods = db.execute(stmt).scalars().all()
    print(f"[DEBUG] Query returned {len(foods)} pending food contributions with status={status}")
    
    # Get User info for all foods in one query to avoid N+1
    user_ids = [f.owner_user_id for f in foods if f.owner_user_id]
    users_dict = {}
    if user_ids:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        users_dict = {user.id: {"username": user.username, "email": user.email} for user in users}
    
    items = []
    for food in foods:
        # Get creator info from users_dict
        user_info = users_dict.get(food.owner_user_id) if food.owner_user_id else None
        username = user_info["username"] if user_info else None
        email = user_info["email"] if user_info else None
        
        # Convert Food to dict và thêm creator info
        food_dict = {
            "id": food.id,
            "owner_user_id": food.owner_user_id,
            "source_code": food.source_code,
            "name": food.name,
            "food_group": food.food_group,
            "is_contribution": food.is_contribution,
            "contribution_status": food.contribution_status,
            "created_at": food.created_at,  # Giữ nguyên datetime object, Pydantic sẽ tự serialize
            "creator_username": username,
            "creator_email": email,
            "portions": [{"id": p.id, "amount": p.amount, "unit": p.unit, "grams": p.grams} for p in food.portions],
            "nutrients": [{"nutrient_name": n.nutrient_name, "unit": n.unit, "amount_per_100g": n.amount_per_100g} for n in food.nutrients]
        }
        items.append(FoodDetail(**food_dict))
    
    return items


@router.get(
    "/contributions/exercises",
    response_model=List[ExerciseResponse],
    summary="Admin - Get Pending Exercise Contributions",
    description="""
    Lấy danh sách các đóng góp bài tập đang chờ duyệt.
    
    **Authorization:** Chỉ admin
    
    **Filtering:**
    - status: pending (mặc định), approved, rejected
    
    **Returns:**
    - Danh sách exercises với is_contribution=true và contribution_status=pending
    - Bao gồm thông tin creator (username, email)
    """
)
def get_pending_exercise_contributions(
    status: str = Query("pending", description="Filter theo status: pending, approved, rejected"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
) -> List[ExerciseResponse]:
    """Lấy danh sách pending exercise contributions"""
    
    # Normalize status để tránh case sensitivity issues
    status = status.lower().strip()
    
    # Query exercises với is_contribution=True và status phù hợp
    # Nếu status là 'pending', cũng bao gồm các record có contribution_status IS NULL
    # (để xử lý các record cũ được tạo trước khi có logic contribution_status)
    if status == 'pending':
        status_filter = or_(
            Exercise.contribution_status == status,
            Exercise.contribution_status.is_(None)
        )
    else:
        status_filter = Exercise.contribution_status == status
    
    # Query Exercise objects first, then get User info separately to avoid Row tuple issues
    stmt = (
        select(Exercise)
        .where(
            and_(
                Exercise.is_contribution == True,
                status_filter,
                Exercise.deleted_at.is_(None)
            )
        )
        .order_by(Exercise.created_at.desc())
    )
    
    exercises = db.execute(stmt).scalars().all()
    
    # Get User info for all exercises in one query to avoid N+1
    user_ids = [e.owner_user_id for e in exercises if e.owner_user_id]
    users_dict = {}
    if user_ids:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        users_dict = {user.id: {"username": user.username, "email": user.email} for user in users}
    
    items = []
    for exercise in exercises:
        # Get creator info from users_dict
        user_info = users_dict.get(exercise.owner_user_id) if exercise.owner_user_id else None
        username = user_info["username"] if user_info else None
        email = user_info["email"] if user_info else None
        
        # Convert Exercise to dict và thêm creator info
        exercise_dict = {
            "id": exercise.id,
            "owner_user_id": exercise.owner_user_id,
            "activity_code": exercise.activity_code,
            "major_heading": exercise.major_heading,
            "description": exercise.description,
            "met_value": exercise.met_value,
            "is_contribution": exercise.is_contribution,
            "contribution_status": exercise.contribution_status,
            "created_at": exercise.created_at,  # Giữ nguyên datetime object, Pydantic sẽ tự serialize
            "creator_username": username,
            "creator_email": email
        }
        items.append(ExerciseResponse(**exercise_dict))
    
    return items


@router.post(
    "/contributions/{type}/{id}/approve",
    summary="Admin - Approve Contribution",
    description="""
    Duyệt một đóng góp (food hoặc exercise).
    
    **Authorization:** Chỉ admin
    
    **Business Logic:**
    - Set contribution_status = 'approved'
    - Item sẽ được hiển thị trong public library
    """
)
def approve_contribution(
    type: str = Path(..., description="Loại: 'foods' hoặc 'exercises'"),
    id: int = Path(..., description="ID của item"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Duyệt contribution"""
    if type == "foods":
        item = db.query(Food).filter(Food.id == id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Food not found")
        if not item.is_contribution:
            raise HTTPException(status_code=400, detail="This food is not a contribution")
        item_name = item.name
        entity_type = "food"
    elif type == "exercises":
        item = db.query(Exercise).filter(Exercise.id == id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Exercise not found")
        if not item.is_contribution:
            raise HTTPException(status_code=400, detail="This exercise is not a contribution")
        item_name = item.description
        entity_type = "exercise"
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Must be 'foods' or 'exercises'")
    
    # Kiểm tra có owner_user_id không
    if not item.owner_user_id:
        raise HTTPException(status_code=400, detail="This contribution has no owner")
    
    # Cập nhật status
    item.contribution_status = 'approved'
    db.commit()
    
    # Tạo notification cho user
    notification = Notification(
        user_id=item.owner_user_id,
        type="approved",
        entity_type=entity_type,
        entity_id=item.id,
        name=item_name,
        is_read=False
    )
    db.add(notification)
    db.commit()
    
    return {"message": "Contribution approved successfully", "id": id, "type": type}


@router.delete(
    "/contributions/{type}/{id}",
    summary="Admin - Reject/Delete Contribution",
    description="""
    Từ chối/xóa một đóng góp (food hoặc exercise).
    
    **Authorization:** Chỉ admin
    
    **Business Logic:**
    - Soft delete: Set deleted_at timestamp
    - Set contribution_status = 'rejected' (nếu muốn giữ lại record)
    - Hoặc xóa hoàn toàn (tùy business logic)
    """
)
def reject_contribution(
    type: str = Path(..., description="Loại: 'foods' hoặc 'exercises'"),
    id: int = Path(..., description="ID của item"),
    reason: Optional[str] = Query(None, description="Lý do từ chối"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Từ chối/xóa contribution"""
    from datetime import datetime, timezone
    
    if type == "foods":
        item = db.query(Food).filter(Food.id == id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Food not found")
        if not item.is_contribution:
            raise HTTPException(status_code=400, detail="This food is not a contribution")
        item_name = item.name
        entity_type = "food"
    elif type == "exercises":
        item = db.query(Exercise).filter(Exercise.id == id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Exercise not found")
        if not item.is_contribution:
            raise HTTPException(status_code=400, detail="This exercise is not a contribution")
        item_name = item.description
        entity_type = "exercise"
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Must be 'foods' or 'exercises'")
    
    # Kiểm tra có owner_user_id không
    if not item.owner_user_id:
        raise HTTPException(status_code=400, detail="This contribution has no owner")
    
    # Soft delete
    item.deleted_at = datetime.now(timezone.utc)
    item.contribution_status = 'rejected'
    db.commit()
    
    # Tạo notification cho user
    notification = Notification(
        user_id=item.owner_user_id,
        type="rejected",
        entity_type=entity_type,
        entity_id=item.id,
        name=item_name,
        reason=reason,
        is_read=False
    )
    db.add(notification)
    db.commit()
    
    return {"message": "Contribution rejected successfully", "id": id, "type": type}


# ==================== DEBUG ENDPOINT ====================

@router.get(
    "/contributions/debug",
    summary="Admin - Debug Contributions (Internal Use)",
    description="""
    Debug endpoint để kiểm tra contributions trong database.
    Chỉ dùng để debug, không dùng trong production.
    """
)
def debug_contributions(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Debug endpoint để kiểm tra contributions"""
    # Tất cả foods với is_contribution=True
    all_foods = db.query(Food).filter(
        Food.is_contribution == True,
        Food.deleted_at.is_(None)
    ).all()
    
    # Tất cả exercises với is_contribution=True
    all_exercises = db.query(Exercise).filter(
        Exercise.is_contribution == True,
        Exercise.deleted_at.is_(None)
    ).all()
    
    return {
        "foods_total": len(all_foods),
        "foods": [
            {
                "id": f.id,
                "name": f.name,
                "is_contribution": f.is_contribution,
                "contribution_status": f.contribution_status,
                "owner_user_id": str(f.owner_user_id) if f.owner_user_id else None,
                "created_at": f.created_at.isoformat() if f.created_at else None
            }
            for f in all_foods[:20]  # Limit 20 items
        ],
        "exercises_total": len(all_exercises),
        "exercises": [
            {
                "id": e.id,
                "description": e.description,
                "is_contribution": e.is_contribution,
                "contribution_status": e.contribution_status,
                "owner_user_id": str(e.owner_user_id) if e.owner_user_id else None,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in all_exercises[:20]  # Limit 20 items
        ]
    }

