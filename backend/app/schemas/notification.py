"""
Pydantic Schemas cho Notifications
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid


# ==================== REQUEST SCHEMAS ====================

class CreateNotificationRequest(BaseModel):
    """Schema để tạo notification mới (admin/system)"""
    user_id: uuid.UUID = Field(..., description="ID người nhận")
    type: str = Field(..., description="Loại thông báo: approved, rejected, deleted, etc.")
    title: Optional[str] = Field(None, description="Tiêu đề")
    message: Optional[str] = Field(None, description="Nội dung")
    entity_type: Optional[str] = Field(None, description="Loại entity: food, exercise, article")
    entity_id: Optional[int] = Field(None, description="ID của entity")
    link: Optional[str] = Field(None, description="Link điều hướng")
    reason: Optional[str] = Field(None, description="Lý do (cho rejected/deleted)")
    name: Optional[str] = Field(None, description="Tên của item")


# ==================== RESPONSE SCHEMAS ====================

class NotificationResponse(BaseModel):
    """Schema response cho 1 notification"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID thông báo")
    type: str = Field(..., description="Loại thông báo")
    title: Optional[str] = Field(None, description="Tiêu đề")
    message: Optional[str] = Field(None, description="Nội dung")
    is_read: bool = Field(..., description="Đã đọc chưa")
    created_at: datetime = Field(..., description="Thời gian tạo")
    entity_type: Optional[str] = Field(None, description="Loại entity")
    entity_id: Optional[int] = Field(None, description="ID entity")
    link: Optional[str] = Field(None, description="Link điều hướng")
    reason: Optional[str] = Field(None, description="Lý do")
    name: Optional[str] = Field(None, description="Tên item")


class NotificationListResponse(BaseModel):
    """Schema response cho danh sách notifications"""
    items: List[NotificationResponse] = Field(..., description="Danh sách thông báo")
    total: int = Field(..., description="Tổng số thông báo")
    unread_count: int = Field(..., description="Số thông báo chưa đọc")

