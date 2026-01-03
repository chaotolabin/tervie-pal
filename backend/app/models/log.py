# Models cho Logs (Food & Exercise tracking)
import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Text, BigInteger, Index, ForeignKey, DateTime, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import text

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
    
    meal_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Loại bữa ăn"
    )

    total_calories: Mapped[Decimal] = mapped_column(
        Numeric(12, 6),
        nullable=False,
        default=0.0,
        comment="Tổng lượng calo của bữa ăn"
    )

    total_protein_g: Mapped[Decimal] = mapped_column(
        Numeric(12, 7),
        nullable=False,
        default=0.0,
        comment="Tổng lượng protein (grams) của bữa ăn"
    )

    total_carbs_g: Mapped[Decimal] = mapped_column(
        Numeric(12, 7),
        nullable=False,
        default=0.0,
        comment="Tổng lượng carbs (grams) của bữa ăn"
    )

    total_fat_g: Mapped[Decimal] = mapped_column(
        Numeric(12, 7),
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
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # meal_type: Mapped["MealType"] = relationship("MealType")
    
    # Indexes
    __table_args__ = (
        Index("ix_food_log_entries_user_id_logged_at", "user_id", "logged_at", postgresql_where=text("deleted_at IS NULL")),
        Index(
            "ix_food_log_entries_user_logged_at_meal_active",
            "user_id", "logged_at", "meal_type",
            postgresql_where=text("deleted_at IS NULL"),
        ),
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
        ForeignKey("foods.id"),      # Không cascade để giữ lịch sử dù food bị xóa
        nullable=False,
        comment="FK tới foods.id"
    )
    
    portion_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("food_portions.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK tới food_portions.id"
    )
    
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        comment="Số lượng (vd: 2 cups, 1.5 servings)"
    )

    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Đơn vị (vd: grams, cups, servings)"
    )
    
    grams: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        comment="Quy đổi về grams để tính dinh dưỡng"
    )
    
    # Snapshot để lịch sử không đổi khi food/portion thay đổi
    calories: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    protein_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 7), nullable=True)
    carbs_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 7), nullable=True)
    fat_g: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 7), nullable=True)
    
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
        CheckConstraint("grams > 0", name="check_food_log_item_grams_positive"),
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

    total_calories: Mapped[Decimal] = mapped_column(
        Numeric(12, 6),
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
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_exercise_log_entries_user_id_logged_at", "user_id", "logged_at", postgresql_where=text("deleted_at IS NULL")),
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

    duration_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Thời gian tập (phút)"
    )

    # strength, condition exercises
    # sets_ex: Mapped[Optional[int]] = mapped_column(
    #     nullable=True,
    #     comment="Số sets"
    # )

    # reps: Mapped[Optional[int]] = mapped_column(
    #     nullable=True,
    #     comment="Số reps mỗi set"
    # )

    # weight_kg: Mapped[Optional[Decimal]] = mapped_column(
    #     nullable=True,
    #     comment="Trọng lượng tạ (kg)"
    # )
    
    # snapshot
    met_value_snapshot: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="MET snapshot tại thời điểm log (copy từ exercises.met_value)"
    )

    # calories: duoc tinh
    calories: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 6),
        nullable=True,
        default=0,
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
        CheckConstraint("duration_min IS NULL OR duration_min > 0", name="ck_ex_item_duration_pos"),
        CheckConstraint("calories >= 0", name="ck_ex_item_calories_nonneg"),
        # CheckConstraint("sets_ex IS NULL OR sets_ex > 0", name="ck_ex_item_sets_pos"),
        # CheckConstraint("reps IS NULL OR reps > 0", name="ck_ex_item_reps_pos"),
        # CheckConstraint("weight_kg IS NULL OR weight_kg >= 0", name="ck_ex_item_weight_nonneg"),
        
        # Tuỳ chọn: bắt buộc phải có duration hoặc sets (ít nhất 1 kiểu log)
        CheckConstraint(
            "duration_min IS NOT NULL OR sets_ex IS NOT NULL",
            name="ck_ex_item_has_input"
        ),
    )