"""
API Routes cho Notifications
Endpoints: GET /notifications, PATCH /notifications/{id}/read, PATCH /notifications/read-all
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    CreateNotificationRequest
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Lấy danh sách thông báo của tôi",
    description="""
    Lấy danh sách tất cả thông báo của user hiện tại.
    
    **Filtering:**
    - unread_only: chỉ lấy thông báo chưa đọc (true/false)
    
    **Pagination:**
    - limit: số lượng items mỗi trang (default: 50, max: 100)
    - cursor: ID của notification cuối cùng trang trước (để load trang tiếp)
    
    **Sorting:**
    - Sắp xếp theo created_at DESC (mới nhất trước)
    """
)
def get_my_notifications(
    limit: int = Query(50, ge=1, le=100, description="Số lượng items mỗi trang"),
    cursor: Optional[int] = Query(None, description="Cursor pagination - ID của item cuối cùng"),
    unread_only: Optional[bool] = Query(None, description="Chỉ lấy thông báo chưa đọc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách thông báo của user hiện tại"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    # Filter unread only
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    # Cursor pagination
    if cursor:
        query = query.filter(Notification.id < cursor)
    
    # Get total count
    total = query.count()
    
    # Get unread count
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    # Order by created_at DESC and limit
    notifications = query.order_by(desc(Notification.created_at)).limit(limit).all()
    
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Đánh dấu thông báo đã đọc",
    description="Đánh dấu một thông báo cụ thể là đã đọc"
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Đánh dấu thông báo đã đọc"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thông báo không tồn tại"
        )
    
    if not notification.is_read:
        notification.is_read = True
        from datetime import datetime, timezone
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    
    return NotificationResponse.model_validate(notification)


@router.patch(
    "/read-all",
    status_code=status.HTTP_200_OK,
    summary="Đánh dấu tất cả thông báo đã đọc",
    description="Đánh dấu tất cả thông báo của user là đã đọc"
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Đánh dấu tất cả thông báo đã đọc"""
    from datetime import datetime, timezone
    
    updated = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({
        Notification.is_read: True,
        Notification.read_at: datetime.now(timezone.utc)
    })
    
    db.commit()
    
    return {
        "message": "Đã đánh dấu tất cả thông báo đã đọc",
        "updated_count": updated
    }


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo thông báo mới (Admin/System)",
    description="Tạo thông báo mới cho user (chỉ dùng bởi admin hoặc system)"
)
def create_notification(
    data: CreateNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo thông báo mới (chỉ admin hoặc system)"""
    # Only admin can create notifications
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền tạo thông báo"
        )
    
    notification = Notification(
        user_id=data.user_id,
        type=data.type,
        title=data.title,
        message=data.message,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        link=data.link,
        reason=data.reason,
        name=data.name,
        is_read=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return NotificationResponse.model_validate(notification)

