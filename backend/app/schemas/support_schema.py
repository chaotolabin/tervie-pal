"""
Pydantic Schemas cho Support Tickets
Chuyển đổi từ OpenAPI spec sang Pydantic models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid

from app.models.support import TicketStatus, TicketCategory


# ==================== REQUEST SCHEMAS ====================

class SupportTicketCreateRequest(BaseModel):
    """Schema để tạo ticket mới"""
    subject: str = Field(
        ...,
        max_length=200,
        description="Tiêu đề ticket",
        example="Lỗi không thể đăng nhập"
    )
    message: str = Field(
        ...,
        max_length=5000,
        description="Nội dung chi tiết",
        example="Tôi không thể đăng nhập vào ứng dụng sau khi cập nhật mật khẩu..."
    )
    category: Optional[str] = Field(
        None,
        description="Phân loại ticket"
    )


class AdminTicketPatchRequest(BaseModel):
    """Schema để admin cập nhật ticket"""
    status: Optional[str] = Field(
        None,
        description="Trạng thái mới"
    )
    category: Optional[str] = Field(
        None,
        description="Category mới"
    )


# ==================== RESPONSE SCHEMAS ====================

class SupportTicketResponse(BaseModel):
    """Schema response cho 1 ticket"""
    id: int = Field(..., description="ID ticket")
    user_id: Optional[uuid.UUID] = Field(None, description="ID người tạo (NULL nếu guest)")
    subject: str = Field(..., description="Tiêu đề")
    message: str = Field(..., description="Nội dung")
    category: Optional[str] = Field(None, description="Phân loại")
    status: str = Field(..., description="Trạng thái")
    created_at: datetime = Field(..., description="Thời gian tạo")
    updated_at: Optional[datetime] = Field(None, description="Thời gian cập nhật")

    class Config:
        from_attributes = True  # Cho phép convert từ SQLAlchemy model


class SupportTicketListResponse(BaseModel):
    """Schema response cho danh sách tickets (có phân trang)"""
    items: List[SupportTicketResponse] = Field(
        ...,
        description="Danh sách tickets"
    )
    next_cursor: Optional[str] = Field(
        None,
        description="Cursor cho trang tiếp theo (ID của ticket cuối cùng)"
    )