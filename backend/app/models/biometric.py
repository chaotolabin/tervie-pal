# Models cho Biometrics Logs
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, DateTime, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.models.base import Base


class BiometricsLog(Base):
    """Bảng biometrics_logs - Nhật ký cân nặng và chiều cao"""
    __tablename__ = "biometrics_logs"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID log"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới users.id"
    )
    
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Thời điểm đo (client gửi)"
    )
    
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Cân nặng (kg). Có thể NULL nếu chỉ cập nhật chiều cao."
    )
    
    height_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Chiều cao (cm). Có thể NULL nếu chỉ cập nhật cân nặng."
    )

    bmi: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        comment="Chỉ số BMI (tính toán từ cân nặng và chiều cao)"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm tạo record (server set)"
    )
    
    # Indexes & Check Constraints
    __table_args__ = (
        Index("ix_biometrics_logs_user_id_logged_at", "user_id", "logged_at"),
        CheckConstraint(
            "weight_kg IS NULL OR weight_kg > 0",
            name="check_weight_positive"
        ),
        CheckConstraint(
            "height_cm IS NULL OR height_cm > 0",
            name="check_height_positive"
        ),
    )

    # Vi du query:
    # SELECT * 
    # FROM biometrics_logs
    # WHERE user_id = ?
    # ORDER BY logged_at DESC