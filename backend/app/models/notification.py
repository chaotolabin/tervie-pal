# Models cho Notifications
import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Text, BigInteger, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey

from app.models.base import Base, TimestampMixin


# Enum cho notification type
class NotificationType(str, enum.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    DELETED = "deleted"
    DELETED_ARTICLE = "deleted_article"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Notification(Base, TimestampMixin):
    """Bảng notifications - Thông báo cho người dùng"""
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID thông báo"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK tới users.id"
    )
    
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Loại thông báo: approved, rejected, deleted, etc."
    )
    
    title: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Tiêu đề thông báo"
    )
    
    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Nội dung thông báo"
    )
    
    is_read: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        comment="Đã đọc chưa"
    )
    
    read_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Thời điểm đọc"
    )
    
    # Metadata for navigation
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Loại entity: food, exercise, article, etc."
    )
    
    entity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="ID của entity liên quan"
    )
    
    link: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Link điều hướng (nếu có)"
    )
    
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Lý do (cho rejected/deleted notifications)"
    )
    
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Tên của item (food name, exercise name, article title, etc.)"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_notifications_user_read", "user_id", "is_read"),
        Index("idx_notifications_created", "created_at"),
    )

