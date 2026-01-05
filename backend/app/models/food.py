# Models cho Foods (Master Data)
import uuid
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import String, Text, BigInteger, Index, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from app.models.base import Base, TimestampMixin


class Food(Base, TimestampMixin):
    """Bảng foods - Master data thực phẩm (global + custom)"""
    __tablename__ = "foods"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,   # Tự động gán id theo thứ tự 
        comment="ID thực phẩm"
    )
    
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="NULL = global data, có giá trị = custom của user"
    )
    
    source_code: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Mã nguồn từ dataset (vd: 01001)"
    )
    
    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Tên thực phẩm"
    )
    
    food_group: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Nhóm thực phẩm (vd: Dairy, Meat)"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Soft delete timestamp"     # Tránh xóa nhầm và cho phép user xem lại nhật kí món đã xóa
    )
    
    is_contribution: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Có phải đóng góp cho cộng đồng không"
    )
    
    contribution_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Trạng thái đóng góp: pending, approved, rejected"
    )
    
    # Relationships (Liên hệ với bảng khác)
    portions: Mapped[List["FoodPortion"]] = relationship(
        "FoodPortion",
        back_populates="food",     # Mối liên hệ 2 chiều 
        cascade="all, delete-orphan"    # Xóa liên tầng, khi xóa food thì xóa luôn portion liên quan
    )
    
    nutrients: Mapped[List["FoodNutrient"]] = relationship(
        "FoodNutrient",
        back_populates="food",
        cascade="all, delete-orphan"
    )
    
    # Indexes & Constraints
    __table_args__ = (
        Index("ix_foods_owner_user_id_name", "owner_user_id", "name", postgresql_where=text("deleted_at IS NULL")),    # Truy vấn theo 2 id này 
        # Unique source_code cho global data
        Index(
            "uq_foods_source_code_global",
            "source_code",
            unique=True,
            postgresql_where=text("owner_user_id IS NULL")
            ),
    )


class FoodPortion(Base, TimestampMixin):
    """Bảng food_portions - Định nghĩa khẩu phần ăn"""
    __tablename__ = "food_portions"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID portion"
    )
    
    food_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("foods.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới foods.id"
    )
    
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        comment="Số lượng (vd: 1, 0.5)"
    )
    
    unit: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Đơn vị (vd: cup, tbsp, piece)"
    )
    
    grams: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        comment="Quy đổi ra grams"
    )
    
    # Relationship
    food: Mapped["Food"] = relationship(
        "Food",
        back_populates="portions"
    )
    
    # Index
    __table_args__ = (
        Index("ix_food_portions_food_id", "food_id"),
        CheckConstraint("amount > 0", name="ck_food_portions_amount_pos"),
        CheckConstraint("grams > 0", name="ck_food_portions_grams_pos"),
    )


class FoodNutrient(Base, TimestampMixin):
    """Bảng food_nutrients - Thông tin dinh dưỡng per 100g"""
    __tablename__ = "food_nutrients"
    
    food_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("foods.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới foods.id"
    )
    
    nutrient_name: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        comment="Tên chất dinh dưỡng (vd: calories, protein)"
    )

    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Đơn vị của chất dinh dưỡng (vd: kcal, g, mg)"
    )
    
    amount_per_100g: Mapped[Decimal] = mapped_column(
        Numeric(14, 6),
        nullable=False,
        comment="Lượng chất dinh dưỡng trên 100g"
    )
    
    # Relationship
    food: Mapped["Food"] = relationship(
        "Food",
        back_populates="nutrients"
    )
    
    __table_args__ = (
        Index("ix_food_nutrients_food_id", "food_id"),
        CheckConstraint("amount_per_100g >= 0", name="ck_food_nutrients_amount_nonneg"),
    )