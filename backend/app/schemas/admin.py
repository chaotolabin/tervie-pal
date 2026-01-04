"""
Admin Schemas - Pydantic models cho Admin Panel
Bao gồm: Dashboard Stats, User Management, Blog Management
"""
from datetime import datetime, date, timezone
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
import uuid


# ==================== DASHBOARD SCHEMAS ====================

class UserStatsResponse(BaseModel):
    """Thống kê người dùng"""
    total_users: int = Field(..., description="Tổng số người dùng")
    new_users: int = Field(..., description="Số người dùng mới trong khoảng thời gian")
    active_users: int = Field(..., description="Số người dùng đang hoạt động")
    admin_count: int = Field(..., description="Số lượng admin")


class LogStatsResponse(BaseModel): 
    """Thống kê logs"""
    total_food_logs: int = Field(..., description="Tổng số bữa ăn đã log")
    total_exercise_logs: int = Field(..., description="Tổng số bài tập đã log")
    food_logs_in_range: int = Field(..., description="Số bữa ăn trong khoảng thời gian")
    exercise_logs_in_range: int = Field(..., description="Số bài tập trong khoảng thời gian")


class RetentionMetricsResponse(BaseModel):
    """Metrics giữ chân người dùng"""
    dau: int = Field(..., description="Daily Active Users (24h)")
    wau: int = Field(..., description="Weekly Active Users (7d)")
    mau: int = Field(..., description="Monthly Active Users (30d)")


class TopPostItem(BaseModel):
    """Item bài viết top"""
    post_id: int
    user_id: uuid.UUID
    title: Optional[str]
    content_preview: str = Field(..., description="100 ký tự đầu của content")
    like_count: int
    save_count: int
    total_engagement: int = Field(..., description="like_count + save_count")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlogStatsResponse(BaseModel):
    """Thống kê blog"""
    total_posts: int = Field(..., description="Tổng số bài viết")
    posts_in_range: int = Field(..., description="Số bài viết trong khoảng thời gian")
    total_likes: int = Field(..., description="Tổng số lượt thích")
    total_saves: int = Field(..., description="Tổng số lượt lưu")
    top_liked_posts: List[TopPostItem] = Field(default_factory=list, description="Top N bài được thích nhiều nhất")
    top_saved_posts: List[TopPostItem] = Field(default_factory=list, description="Top N bài được lưu nhiều nhất")
    top_engagement_posts: List[TopPostItem] = Field(default_factory=list, description="Top N bài có tổng tương tác cao nhất")
    trending_posts: List[TopPostItem] = Field(default_factory=list, description="Top N bài trending gần đây")


class StreakUserItem(BaseModel):
    """User với streak info"""
    user_id: uuid.UUID
    username: str
    email: str
    current_streak: int
    longest_streak: int

    model_config = ConfigDict(from_attributes=True)


class StreakStatsResponse(BaseModel):
    """Thống kê streak"""
    users_with_streak: int = Field(..., description="Số users có streak > 0")
    average_streak: float = Field(..., description="Streak trung bình")
    highest_streak: int = Field(..., description="Streak cao nhất")
    highest_streak_user_id: Optional[uuid.UUID] = Field(None, description="User có streak cao nhất")
    top_streak_users: List[StreakUserItem] = Field(default_factory=list, description="Top N users có streak cao nhất")
    users_with_week_streak: int = Field(..., description="Số users có streak >= 7")
    users_with_month_streak: int = Field(..., description="Số users có streak >= 30")


class AdminDashboardStatsResponse(BaseModel):
    """Response tổng hợp cho Dashboard"""
    user_stats: UserStatsResponse
    log_stats: LogStatsResponse
    retention_metrics: RetentionMetricsResponse
    blog_stats: BlogStatsResponse
    streak_stats: StreakStatsResponse
    query_range: str = Field(..., description="Khoảng thời gian query: 7d, 30d, 90d")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CoreDashboardResponse(BaseModel):
    """Dashboard Core - User, Log, Retention metrics"""
    user_stats: UserStatsResponse
    log_stats: LogStatsResponse
    retention_metrics: RetentionMetricsResponse
    query_range: str = Field(..., description="Khoảng thời gian query: 7d, 30d, 90d")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BlogDashboardResponse(BaseModel):
    """Dashboard Blog - Blog & Community metrics"""
    blog_stats: BlogStatsResponse
    query_range: str = Field(..., description="Khoảng thời gian query: 7d, 30d, 90d")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StreakDashboardResponse(BaseModel):
    """Dashboard Streak - Streak metrics"""
    streak_stats: StreakStatsResponse
    query_range: str = Field(..., description="Khoảng thời gian query: 7d, 30d, 90d")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== USER MANAGEMENT SCHEMAS ====================

class AdminUserListItem(BaseModel):
    """Item trong danh sách users (Admin view)"""
    id: uuid.UUID
    username: str
    email: str
    role: str
    full_name: Optional[str]
    created_at: datetime
    current_streak: int = Field(default=0, description="Streak hiện tại")
    last_log_at: Optional[datetime] = Field(None, description="Lần cuối hoạt động (log thức ăn/bài tập)")

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    """Response danh sách users với pagination"""
    items: List[AdminUserListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserActivitySummary(BaseModel):
    """Tóm tắt hoạt động của user"""
    total_food_logs: int
    total_exercise_logs: int
    total_posts: int
    last_food_log_at: Optional[datetime]
    last_exercise_log_at: Optional[datetime]
    last_post_at: Optional[datetime]


class AdminUserDetailResponse(BaseModel):
    """Chi tiết user (Admin view)"""
    # Basic info
    id: uuid.UUID
    username: str
    email: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Profile
    full_name: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[date]
    height_cm_default: Optional[Decimal]
    
    # Status
    password_changed_at: Optional[datetime]
    
    # Streak
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_on_time_day: Optional[date]
    
    # Activity
    activity_summary: UserActivitySummary
    
    # Goal
    goal_type: Optional[str]
    daily_calorie_target: Optional[Decimal]
    
    model_config = ConfigDict(from_attributes=True)


class UserRolePatchRequest(BaseModel):
    """Request để thay đổi role"""
    role: str = Field(..., pattern="^(user|admin)$", description="Role: user hoặc admin")


class StreakAdjustRequest(BaseModel):
    """Request để điều chỉnh streak"""
    current_streak: int = Field(..., ge=0, description="Streak mới")
    reason: str = Field(..., min_length=1, max_length=500, description="Lý do điều chỉnh")


# ==================== BLOG MANAGEMENT SCHEMAS ====================

class AdminPostListItem(BaseModel):
    """Item bài viết trong danh sách (Admin view)"""
    id: int
    user_id: uuid.UUID
    username: str
    title: Optional[str]
    content_preview: str
    like_count: int
    save_count: int
    created_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class AdminPostListResponse(BaseModel):
    """Response danh sách bài viết (Admin)"""
    items: List[AdminPostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class PostDeleteRequest(BaseModel):
    """Request xóa bài viết"""
    reason: Optional[str] = Field(None, max_length=500, description="Lý do xóa")


# ==================== COMMON SCHEMAS ====================

class AdminActionResponse(BaseModel):
    """Response chung cho các action của admin"""
    success: bool
    message: str
    action: str = Field(..., description="Loại action: adjust_streak, delete_post, update_role...")
    performed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    performed_by: uuid.UUID = Field(..., description="Admin ID thực hiện")


class AdminSimpleDashboardResponse(BaseModel):
    """Response đơn giản cho dashboard summary (openapi spec)"""
    users_count: int = Field(..., ge=0)
    posts_count: int = Field(..., ge=0)
    open_tickets_count: int = Field(..., ge=0)


# ==================== DAILY STATS SCHEMAS ====================

class DailyStatItem(BaseModel):
    """Thống kê của 1 ngày"""
    date_log: date = Field(..., description="Ngày thống kê")
    
    # User metrics
    total_users: int = Field(..., description="Tổng số user (tích lũy)")
    new_users: int = Field(..., description="User đăng ký mới")
    active_users: int = Field(..., description="DAU - có log trong ngày - food hoặc exercise")
    active_food_users: int = Field(..., description="User có log ăn")
    active_exercise_users: int = Field(..., description="User có log tập")
    
    # Volume metrics
    total_food_logs: int = Field(..., description="Số food logs")
    total_exercise_logs: int = Field(..., description="Số exercise logs")
    
    # Community metrics
    new_posts: int = Field(..., description="Bài blog mới")
    total_likes: int = Field(..., description="Lượt like")
    total_saves: int = Field(..., description="Lượt save")
    new_tickets: int = Field(..., description="Ticket mới")
    
    # Health metrics
    users_hit_calorie_target: int = Field(..., description="User đạt calorie goal")
    avg_streak_length: Decimal = Field(..., description="Streak trung bình")
    
    created_at: datetime = Field(..., description="Thời điểm tạo record")
    
    model_config = ConfigDict(from_attributes=True)


class DailyStatsResponse(BaseModel):
    """Response danh sách daily stats"""
    items: List[DailyStatItem] = Field(..., description="Danh sách stats theo ngày")
    total_days: int = Field(..., description="Số ngày có dữ liệu")
    date_from: date = Field(..., description="Ngày bắt đầu")
    date_to: date = Field(..., description="Ngày kết thúc")