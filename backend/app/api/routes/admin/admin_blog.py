"""
API Routes cho Admin Blog Management
Endpoints: List posts, Delete post
"""
from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.auth import User
from app.schemas.admin import (
    AdminPostListResponse,
    AdminPostListItem,
    PostDeleteRequest,
    AdminActionResponse
)
from app.services.admin.admin_blog_service import AdminBlogService


router = APIRouter()


# ==================== BLOG MANAGEMENT ENDPOINTS ====================

@router.get(
    "/posts",
    response_model=AdminPostListResponse,
    summary="Admin - List All Posts",
    description="""
    Lấy danh sách tất cả posts trong hệ thống.
    
    **Authorization:** Chỉ admin
    
    **Features:**
    - Phân trang
    - Có thể xem cả posts đã xóa (soft deleted)
    - Hiển thị username, like_count, save_count
    
    **Use Cases:**
    - Xem tất cả bài viết để kiểm duyệt
    - Tìm bài viết vi phạm
    - Thống kê engagement
    """
)
def list_posts(
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    page_size: int = Query(50, ge=1, le=200, description="Số items mỗi trang"),
    include_deleted: bool = Query(False, description="Bao gồm cả posts đã xóa"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    List posts với admin view
    
    **Security:** Chỉ admin
    """
    items, total = AdminBlogService.get_posts_list(
        db=db,
        page=page,
        page_size=page_size,
        include_deleted=include_deleted
    )
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    # Convert dict items to Pydantic models
    post_items = [AdminPostListItem(**item) for item in items]
    
    return AdminPostListResponse(
        items=post_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.delete(
    "/posts/{post_id}",
    response_model=AdminActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin - Delete Post",
    description="""
    Xóa bài viết (soft delete).
    
    **Authorization:** Chỉ admin
    
    **Business Logic:**
    - Soft delete: Set deleted_at timestamp
    - Không xóa thật khỏi database
    - Ghi log lý do xóa (audit trail)
    
    **Use Cases:**
    - Xóa bài viết vi phạm quy định
    - Xóa spam
    - Xóa nội dung không phù hợp
    """
)
def delete_post(
    post_id: int = Path(..., description="Post ID", ge=1),
    data: Optional[PostDeleteRequest] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Soft delete post
    
    **Security:** Chỉ admin
    **Audit:** Ghi log reason và admin thực hiện
    """
    reason = data.reason if data else None
    
    deleted_post = AdminBlogService.delete_post(
        db=db,
        post_id=post_id,
        reason=reason,
        admin_id=admin_user.id
    )
    
    return AdminActionResponse(
        success=True,
        message=f"Post {post_id} deleted. Reason: {reason or 'No reason provided'}",
        action="delete_post",
        performed_by=admin_user.id
    )


@router.post(
    "/posts/{post_id}/restore",
    response_model=AdminActionResponse,
    summary="Admin - Restore Deleted Post (TODO)",
    description="""
    Khôi phục bài viết đã xóa.
    
    **Authorization:** Chỉ admin
    
    **TODO:** Implement restore logic
    - Set deleted_at = NULL
    - Ghi log action
    """
)
def restore_post(
    post_id: int = Path(..., description="Post ID", ge=1),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Restore deleted post
    
    **TODO:** Implement restore logic
    """
    # TODO: Implement
    return AdminActionResponse(
        success=False,
        message="Restore post feature not implemented yet",
        action="restore_post",
        performed_by=admin_user.id
    )
