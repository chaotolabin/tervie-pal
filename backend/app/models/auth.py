# Models cho Identity & Authentication
import enum
import uuid
from datetime import datetime, timezone, date
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import Text, Date, DateTime, BigInteger, Index, CheckConstraint, ForeignKey, text, Numeric
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.models.base import Base, TimestampMixin


# Enum cho user role
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

# Enum cho gender, can biet male va female de tinh toan cac chi so (BMR)
class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

# Enum cho goal type
class GoalType(str, enum.Enum):
    LOSE_WEIGHT = "lose_weight"
    GAIN_WEIGHT = "gain_weight"
    MAINTAIN_WEIGHT = "maintain_weight"
    BUILD_MUSCLE = "build_muscle"
    IMPROVE_HEALTH = "improve_health"


class User(Base, TimestampMixin):
    """Bảng users - Thông tin đăng nhập và xác thực"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="ID người dùng (UUID)"
    )
    
    username: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        comment="Tên đăng nhập (unique)"
    )
    
    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        comment="Email (unique)"
        # Co the them index=True neu can thiet tim kiem nhanh, chu chua hieu lam
    )
    
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mật khẩu đã hash (bcrypt/argon2)"
    )
    
    role: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="user",
        server_default="user",
        comment="Vai trò: user hoặc admin"
    )
    
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Thời điểm thay đổi password (để revoke tokens)"
    )
    
    # Relationships
    profile: Mapped[Optional["Profile"]] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    refresh_sessions: Mapped[List["RefreshSession"]] = relationship(
        "RefreshSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    goal: Mapped[Optional["Goal"]] = relationship(
        "Goal",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Profile(Base, TimestampMixin):
    """Bảng profiles - Thông tin cá nhân người dùng"""
    __tablename__ = "profiles"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới users.id"
    )
    
    full_name: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Họ và tên đầy đủ"
    )
    
    gender: Mapped[Optional[str]] = mapped_column(
        # String(30),
        Text,
        nullable=True,
        comment="Giới tính: male, female"
    )
    
    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date,  # DATE type
        nullable=True,
        comment="Ngày sinh"
    )
    
    height_cm_default: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Chiều cao mặc định (cm)"
    )
    
    # avatar_url: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="URL ảnh đại diện"
    # )
    
    # timezone: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="Múi giờ người dùng (vd: Asia/Ho_Chi_Minh)"
    # )
    
    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        foreign_keys=[user_id]
    )

    __table_args__ = (
        CheckConstraint(
            "height_cm_default IS NULL OR height_cm_default > 0",
            name="check_height_positive"
        ),
    )


class RefreshSession(Base):
    """Bảng refresh_sessions - Quản lý refresh tokens per device"""
    __tablename__ = "refresh_sessions"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID session"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"), # CASCADE khi xoa user, profile va refresh sessions cung bi xoa
        nullable=False,
        comment="FK tới users.id"
    )
    
    refresh_token_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        comment="Hash của refresh token"
    )
    
    device_label: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Nhãn thiết bị (vd: iPhone 13)"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User agent string"
    )
    
    ip: Mapped[Optional[str]] = mapped_column(
        INET,  # PostgreSQL INET type
        nullable=True,
        comment="Địa chỉ IP"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm tạo session"
    )
    
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Lần cuối sử dụng token"
    )
    
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Thời điểm revoke token (logout hoặc đổi password)"
    )
    
    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_sessions",
        foreign_keys=[user_id]
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_refresh_sessions_user_id", "user_id", postgresql_where=text("revoked_at IS NULL")),
    )


class Goal(Base, TimestampMixin):
    """Bảng goals - Mục tiêu sức khỏe của người dùng (1 user = 1 goal active)"""
    __tablename__ = "goals"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới users.id, đồng thời là PK (1 user = 1 goal active)"
    )
    
    goal_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Loại mục tiêu: lose_weight, gain_weight, maintain_weight, build_muscle, improve_health"
    )
    
    baseline_activity: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default="low_active",
        comment="Mức độ hoạt động: sedentary, low_active, moderately_active, very_active, extremely_active"
    )
    
    weekly_goal: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        default=0.5,
        comment="Mục tiêu kg/tuần (0.25 - 1.0) cho lose/gain weight"
    )
    
    target_weight_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Cân nặng mục tiêu (kg) - chỉ dùng khi lose/gain weight"
    )
    
    daily_calorie_target: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
        comment="Tổng năng lượng mục tiêu mỗi ngày (kcal)"
    )
    
    protein_grams: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="Lượng protein mục tiêu (grams) - tính từ daily_calorie × ratio ÷ 4"
    )
    
    fat_grams: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="Lượng fat mục tiêu (grams) - tính từ daily_calorie × ratio ÷ 9"
    )
    
    carb_grams: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="Lượng carbs mục tiêu (grams) - tính từ daily_calorie × ratio ÷ 4"
    )
    
    weekly_exercise_min: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Số phút vận động mục tiêu mỗi tuần (ví dụ: 150)"
    )
    
    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="goal",
        foreign_keys=[user_id]
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "target_weight_kg IS NULL OR target_weight_kg > 0",
            name="check_target_weight_positive"
        ),
        CheckConstraint(
            "daily_calorie_target > 0",
            name="check_calorie_positive"
        ),
        CheckConstraint(
            "protein_grams IS NULL OR protein_grams >= 0",
            name="check_protein_grams_positive"
        ),
        CheckConstraint(
            "fat_grams IS NULL OR fat_grams >= 0",
            name="check_fat_grams_positive"
        ),
        CheckConstraint(
            "carb_grams IS NULL OR carb_grams >= 0",
            name="check_carb_grams_positive"
        ),
        CheckConstraint(
            "weekly_exercise_min IS NULL OR weekly_exercise_min >= 0",
            name="check_exercise_min_positive"
        ),
    )