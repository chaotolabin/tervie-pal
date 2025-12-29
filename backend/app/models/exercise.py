# Models cho Exercises (Master Data)
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Text, BigInteger, Integer, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Exercise(Base, TimestampMixin):
    """Bảng exercises - Master data bài tập (global + custom)"""
    __tablename__ = "exercises"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID bài tập"
    )
    
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="NULL = global data, có giá trị = custom của user"
    )
    
    activity_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Mã hoạt động từ dataset"
    )
    
    major_heading: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Nhóm bài tập chính (vd: Running, Swimming)"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mô tả bài tập"
    )
    
    met_value: Mapped[float] = mapped_column(
        nullable=False,
        comment="Giá trị MET (Metabolic Equivalent) - năng lượng tiêu hao"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Soft delete timestamp"
    )
    
    # Indexes & Constraints
    __table_args__ = (
        Index("ix_exercises_owner_user_id_description", "owner_user_id", "description"),
        # Unique activity_code cho global data
        UniqueConstraint(
            "activity_code",
            name="uq_exercises_activity_code_global",
            postgresql_where="owner_user_id IS NULL"
        ),
    )