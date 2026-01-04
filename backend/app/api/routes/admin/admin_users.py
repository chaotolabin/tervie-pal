"""
API Routes cho Admin User Management
Endpoints: GET/PATCH users, adjust streak
"""
from typing import Optional
import uuid
from math import ceil
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.auth import User
from app.schemas.admin import (
    AdminUserListResponse,
    AdminUserDetailResponse,
    UserRolePatchRequest,
    StreakAdjustRequest,
    AdminActionResponse
)
from app.services.admin.admin_user_service import AdminUserService


router = APIRouter()


# ==================== USER MANAGEMENT ENDPOINTS ====================

@router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="Admin - List Users",
    description="""
    Lấy danh sách tất cả users với phân trang và filter.
    
    **Authorization:** Chỉ admin
    
    **Filters:**
    - email: Tìm theo email (partial match)
    - role: Filter theo role (user/admin)
    
    **Pagination:**
    - page: Trang hiện tại (default: 1)
    - page_size: Số items mỗi trang (default: 50, max: 200)
    
    **Response:**
    - Danh sách users với thông tin cơ bản
    - Streak hiện tại
    - Last active time
    """
)
def list_users(
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    page_size: int = Query(50, ge=1, le=200, description="Số items mỗi trang"),
    email: Optional[str] = Query(None, description="Filter theo email"),
    role: Optional[str] = Query(None, regex="^(user|admin)$", description="Filter theo role"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    List users với phân trang và filter
    
    **Security:** Chỉ admin
    """
    items, total = AdminUserService.get_users_list(
        db=db,
        page=page,
        page_size=page_size,
        email_filter=email,
        role_filter=role
    )
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return AdminUserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetailResponse,
    summary="Admin - Get User Detail",
    description="""
    Lấy chi tiết đầy đủ của một user.
    
    **Authorization:** Chỉ admin
    
    **Returns:**
    - Thông tin cá nhân (profile, goal)
    - Streak stats
    - Activity summary (số logs, posts, last activity)
    - Account status
    """
)
def get_user_detail(
    user_id: uuid.UUID = Path(..., description="User ID"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Chi tiết user (Admin view)
    
    **Security:** Chỉ admin
    """
    user_detail = AdminUserService.get_user_detail(db, user_id)
    return AdminUserDetailResponse(**user_detail)


@router.patch(
    "/users/{user_id}/role",
    response_model=AdminActionResponse,
    summary="Admin - Update User Role",
    description="""
    Thay đổi role của user (user <-> admin).
    
    **Authorization:** Chỉ admin
    
    **Business Rules:**
    - Admin không thể thay đổi role của chính mình
    - Cần ghi log action (TODO: audit log)
    
    **Use Cases:**
    - Promote user lên admin
    - Demote admin xuống user
    """
)
def update_user_role(
    user_id: uuid.UUID = Path(..., description="User ID"),
    data: UserRolePatchRequest = ...,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Cập nhật role của user
    
    **Security:** Chỉ admin, không thể tự đổi role
    """
    updated_user = AdminUserService.update_user_role(
        db=db,
        user_id=user_id,
        new_role=data.role,
        admin_id=admin_user.id
    )
    
    return AdminActionResponse(
        success=True,
        message=f"User role updated to {data.role}",
        action="update_user_role",
        performed_by=admin_user.id
    )


@router.post(
    "/users/{user_id}/streak/adjust",
    response_model=AdminActionResponse,
    summary="Admin - Adjust User Streak",
    description="""
    Điều chỉnh streak của user (xử lý khiếu nại, sửa lỗi).
    
    **Authorization:** Chỉ admin
    
    **Business Logic:**
    - Cho phép set streak thủ công
    - Tự động cập nhật longest_streak nếu cần
    - Ghi log lý do điều chỉnh (audit trail)
    
    **Use Cases:**
    - User khiếu nại streak bị mất do lỗi hệ thống
    - Sửa lỗi tính toán streak
    - Thưởng streak cho sự kiện đặc biệt
    """
)
def adjust_user_streak(
    user_id: uuid.UUID = Path(..., description="User ID"),
    data: StreakAdjustRequest = ...,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Điều chỉnh streak của user
    
    **Security:** Chỉ admin
    **Audit:** Ghi log lý do và admin thực hiện
    """
    streak_state = AdminUserService.adjust_user_streak(
        db=db,
        user_id=user_id,
        new_streak=data.current_streak,
        reason=data.reason,
        admin_id=admin_user.id
    )
    
    return AdminActionResponse(
        success=True,
        message=f"Streak adjusted to {data.current_streak}. Reason: {data.reason}",
        action="adjust_streak",
        performed_by=admin_user.id
    )



