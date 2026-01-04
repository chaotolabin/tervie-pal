# Models cho Streak Cache
import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy import Enum as SQLEnum

from app.models.base import Base


# Enum cho streak status
class StreakStatus(str, enum.Enum):
    GREEN = "green"  # Hoàn thành mục tiêu đúng hạn
    YELLOW = "yellow"  # Hoàn thành trễ
    NONE = "none"  # Không hoàn thành (không lưu vào DB, chỉ tính runtime)


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
        comment="Ngày (không có giờ) (YYYY-MM-DD)"
    )
    
    status: Mapped[StreakStatus] = mapped_column(
        # String(20),
        SQLEnum(
            StreakStatus, 
            name="streak_status_enum", 
            create_type=False,
            values_callable=lambda x: [e.value for e in x]  # Đảm bảo sử dụng enum value
        ),
        nullable=False,
        comment="Trạng thái: green (on-time), yellow (late)"
    )

    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm cập nhật cuối"
    )
    
    __table_args__ = (
        Index("ix_streak_days_cache_user_day", "day"),
    )

    
# Để không phải tính toán lại toàn bộ streak hiện tại mỗi lần truy vấn,
class UserStreakState(Base):
    """Bảng user_streak_state - Trạng thái streak hiện tại của người dùng"""
    __tablename__ = "user_streak_state"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Ngày cuối hoạt động để tính streak
    last_on_time_day: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
