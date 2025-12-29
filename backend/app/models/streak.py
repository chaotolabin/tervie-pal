# Models cho Streak Cache
from ast import Index
import enum
import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Date, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy import Enum as SQLEnum

from app.models.base import Base


# Enum cho streak status
class StreakStatus(str, enum.Enum):
    GREEN = "green"  # Hoàn thành mục tiêu
    YELLOW = "yellow"  # Hoàn thành một phần
    NONE = "none"  # Không hoạt động


class StreakDayCache(Base):
    """Bảng streak_days_cache - Cache trạng thái streak theo ngày"""
    __tablename__ = "streak_days_cache"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới users.id"
    )
    
    day: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        comment="Ngày (không có giờ)"
    )
    
    status: Mapped[StreakStatus] = mapped_column(
        # String(20),
        SQLEnum(StreakStatus, name="streak_status_enum"),
        nullable=False,
        comment="Trạng thái: green (đạt), yellow (1 phần), none (không)"
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Số ngày streak liên tiếp tính đến ngày này"
    )

    longest_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Số ngày streak liên tiếp dài nhất tính đến ngày này"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm cập nhật cuối"
    )

    # co the them index de thong ke theo status trong ngay
    # Index("ix_streak_day_status", "day", "status")