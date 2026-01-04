"""
Admin Statistics Models
Model để lưu trữ thống kê hệ thống theo ngày
"""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Integer, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class DailySystemStat(Base):
    """
    Bảng lưu snapshot thống kê hệ thống theo ngày
    
    Primary Key: date_log (mỗi ngày 1 dòng duy nhất)
    Use Case: Vẽ biểu đồ dashboard, phân tích xu hướng tăng trưởng
    """
    __tablename__ = "daily_system_stats"

    # ================= ĐỊNH DANH =================
    date_log: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        index=True,
        comment="Ngày thống kê"
    )

    # ================= NHÓM 1: USER & TĂNG TRƯỞNG =================
    total_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Tổng số user trong hệ thống (tích lũy) tính đến cuối ngày"
    )
    
    new_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số user đăng ký mới trong ngày"
    )

    # ================= NHÓM 2: ACTIVE (RETENTION) =================
    active_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="DAU - Daily Active Users (có ít nhất 1 food_log hoặc exercise_log trong ngày)"
    )
    
    active_food_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số user có log ăn trong ngày"
    )
    
    active_exercise_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số user có log tập trong ngày"
    )

    # ================= NHÓM 3: VOLUME (KHỐI LƯỢNG LOGS) =================
    total_food_logs: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số food log entries tạo mới trong ngày"
    )
    
    total_exercise_logs: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số exercise log entries tạo mới trong ngày"
    )

    # ================= NHÓM 4: BLOG & COMMUNITY =================
    new_posts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số bài blog mới đăng trong ngày"
    )
    
    total_likes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số lượt like phát sinh trong ngày"
    )
    
    total_saves: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số lượt save phát sinh trong ngày"
    )

    # ================= NHÓM 5: VẬN HÀNH & HỖ TRỢ =================
    new_tickets: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số ticket support mới trong ngày"
    )

    # ================= NHÓM 6: CHẤT LƯỢNG (HEALTH IMPACT) =================
    users_hit_calorie_target: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Số user ăn đúng calorie goal (+/- 10%)"
    )
    
    avg_streak_length: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Streak trung bình của active users trong ngày"
    )

    # ================= METADATA =================
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Thời điểm chạy job thống kê - cuối ngày"
    )

    def __repr__(self):
        return f"<DailySystemStat(date_log={self.date_log}, users={self.total_users}, dau={self.active_users})>"