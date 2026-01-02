# Models cho Support Tickets
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


# Enum cho ticket status
class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

# Enum cho category ticket (bug, feature_request, question)
class TicketCategory(str, enum.Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request" # lien quan den tinh nang moi
    QUESTION = "question"
    OTHER = "other"


class SupportTicket(Base, TimestampMixin):
    """Bảng support_tickets - Yêu cầu hỗ trợ từ người dùng"""
    __tablename__ = "support_tickets"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID ticket"
    )
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK tới users.id (NULL nếu guest)"
    )
    
    subject: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Tiêu đề ticket"
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Nội dung chi tiết"
    )
    
    category: Mapped[TicketCategory] = mapped_column(
        SQLEnum(TicketCategory, name="ticket_category_enum"),
        nullable=True,
        comment="Phân loại ticket"
    )
    
    status: Mapped[TicketStatus] = mapped_column(
        # String(20),
        SQLEnum(TicketStatus, name="ticket_status_enum"),
        nullable=False,
        default=TicketStatus.OPEN,
        server_default=TicketStatus.OPEN.value,
        comment="Trạng thái xử lý"
    )

    __table_args__ = (
        Index("ix_support_ticket_status", "status"), 
        Index("ix_support_ticket_category", "category"),
    )