# Models cho Logs (Food & Exercise tracking)
import enum
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, SmallInteger, BigInteger, Index, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.models.base import Base, TimestampMixin


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACKS = "snacks"

class FoodLogEntry(Base, TimestampMixin):
    """Bảng food_log_entries - Nhật ký bữa ăn (entry level)"""
    __tablename__ = "food_log_entries"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID entry"
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
        comment="Thời điểm người dùng log bữa ăn (client gửi)"
    )
    
    meal_type: Mapped[MealType] = mapped_column(
        SQLEnum(MealType, name="meal_type_enum"),
        nullable=False,
        comment="Loại bữa ăn"
    )

    total_calories: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Tổng lượng calo của bữa ăn"
    )

    total_protein_g: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Tổng lượng protein (grams) của bữa ăn"
    )

    total_carbs_g: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Tổng lượng carbs (grams) của bữa ăn"
    )

    total_fat_g: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Tổng lượng fat (grams) của bữa ăn"
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )
    
    # Relationships
    items: Mapped[List["FoodLogItem"]] = relationship(
        "FoodLogItem",
        back_populates="entry",
        cascade="all, delete-orphan"
    )
    
    # meal_type: Mapped["MealType"] = relationship("MealType")
    
    # Indexes
    __table_args__ = (
        Index("ix_food_log_entries_user_id_logged_at", "user_id", "logged_at"),
    )


class FoodLogItem(Base):
    """Bảng food_log_items - Chi tiết thực phẩm trong bữa ăn"""
    __tablename__ = "food_log_items"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID item"
    )
    
    entry_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("food_log_entries.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới food_log_entries.id"
    )
    
    food_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("foods.id"),
        nullable=False,
        comment="FK tới foods.id"
    )
    
    portion_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("food_portions.id"),
        nullable=True,
        comment="FK tới food_portions.id"
    )
    
    quantity: Mapped[float] = mapped_column(
        nullable=False,
        comment="Số lượng (vd: 2 cups, 1.5 servings)"
    )

    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Đơn vị (vd: grams, cups, servings)"
    )
    
    grams: Mapped[float] = mapped_column(
        nullable=False,
        comment="Quy đổi về grams để tính dinh dưỡng"
    )
    
    # Relationships
    entry: Mapped["FoodLogEntry"] = relationship(
        "FoodLogEntry",
        back_populates="items"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_food_log_items_entry_id", "entry_id"),
        Index("ix_food_log_items_food_id", "food_id"),
        CheckConstraint("quantity > 0", name="check_food_log_item_quantity_positive"),
    )


class ExerciseLogEntry(Base, TimestampMixin):
    """Bảng exercise_log_entries - Nhật ký tập luyện (entry level)"""
    __tablename__ = "exercise_log_entries"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID entry"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới users.id"
    )

    total_calories: Mapped[Optional[float]] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Tổng lượng calo tiêu hao của bài tập"
    )

    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Thời điểm người dùng log bài tập (client gửi)"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )
    
    # Relationships
    items: Mapped[List["ExerciseLogItem"]] = relationship(
        "ExerciseLogItem",
        back_populates="entry",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_exercise_log_entries_user_id_logged_at", "user_id", "logged_at"),
    )


class ExerciseLogItem(Base):
    """Bảng exercise_log_items - Chi tiết bài tập"""
    __tablename__ = "exercise_log_items"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID item"
    )
    
    entry_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("exercise_log_entries.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới exercise_log_entries.id"
    )
    
    exercise_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("exercises.id"),
        nullable=False,
        comment="FK tới exercises.id"
    )
    
    # cai nay can xem lai bo du lieu met 1 chut de xem dat truong nhu the nao cho hop ly
    # vi du web Cronometer nguoi ta dung Effort Level voi duration de tinh met
    # hay minh dua vao exercises.id a :(?

    duration_min: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Thời gian tập (phút)"
    )

    # strength, condition exercises
    sets_ex: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Số sets"
    )

    reps: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Số reps mỗi set"
    )

    weight_kg: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Trọng lượng tạ (kg)"
    )

    # calories: duoc tinh
    calories: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Lượng calo tiêu hao (nếu có)"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Ghi chú thêm"
    )
    
    # Relationships
    entry: Mapped["ExerciseLogEntry"] = relationship(
        "ExerciseLogEntry",
        back_populates="items"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_exercise_log_items_entry_id", "entry_id"),
        Index("ix_exercise_log_items_exercise_id", "exercise_id"),
    )