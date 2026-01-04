"""
API Routes cho Admin Dashboard (Statistics)
Endpoint: GET /admin/dashboard/stats
"""
from datetime import datetime, timezone, timedelta, date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.auth import User
from app.models.support import SupportTicket
from app.schemas.admin import (
    AdminDashboardStatsResponse,
    AdminSimpleDashboardResponse,
    DailyStatsResponse,
    CoreDashboardResponse,
    BlogDashboardResponse,
    StreakDashboardResponse
)
from app.services.admin.admin_dashboard_service import AdminDashboardService
from sqlalchemy import func


router = APIRouter()


# ==================== DASHBOARD ENDPOINTS ====================

@router.get(
    "/dashboard/stats",
    response_model=AdminDashboardStatsResponse,
    summary="Admin - Dashboard Statistics (Chi tiết)",
    description="""
    Lấy thống kê toàn diện cho Admin Dashboard.
    
    **Authorization:** Chỉ admin
    
    **Query Parameters:**
    - range: 7d (mặc định), 30d, 90d
    - top_n: Số lượng items trong các top lists (default: 10)
    
    **Returns:**
    - User Stats: Tổng users, users mới, active users
    - Log Stats: Tổng food/exercise logs
    - Retention: DAU, WAU, MAU
    - Blog Stats: Posts, likes, saves, top posts
    - Streak Stats: Users với streak, top streak users
    """
)
def get_dashboard_stats(
    range: str = Query(
        "7d",
        regex="^(7d|30d|90d)$",
        description="Khoảng thời gian: 7d, 30d, 90d"
    ),
    top_n: int = Query(
        10,
        ge=1,
        le=50,
        description="Số lượng items trong top lists"
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Lấy thống kê dashboard chi tiết
    
    **Security:** Chỉ admin mới có quyền truy cập
    """
    # Parse range
    range_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90
    }
    range_days = range_map[range]
    range_start = datetime.now(timezone.utc) - timedelta(days=range_days)
    
    # Gọi các service methods
    user_stats = AdminDashboardService.get_user_stats(db, range_days, range_start)
    log_stats = AdminDashboardService.get_log_stats(db, range_start)
    retention_metrics = AdminDashboardService.get_retention_metrics(db)
    blog_stats = AdminDashboardService.get_blog_stats(db, range_start, top_n)
    streak_stats = AdminDashboardService.get_streak_stats(db, top_n)
    
    return AdminDashboardStatsResponse(
        user_stats=user_stats,
        log_stats=log_stats,
        retention_metrics=retention_metrics,
        blog_stats=blog_stats,
        streak_stats=streak_stats,
        query_range=range,
        generated_at=datetime.now(timezone.utc)
    )


@router.get(
    "/dashboard",
    response_model=AdminSimpleDashboardResponse,
    summary="Admin - Dashboard Summary (Đơn giản)",
    description="""
    Dashboard summary đơn giản theo OpenAPI spec.
    
    **Authorization:** Chỉ admin
    
    **Returns:**
    - users_count: Tổng số users
    - posts_count: Tổng số posts
    - open_tickets_count: Số tickets đang mở
    """
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Dashboard summary đơn giản
    
    **Tuân theo spec trong openapi-draft.yaml**
    """
    # Count users
    users_count = db.query(func.count(User.id)).scalar() or 0
    
    # Count posts (not deleted)
    from app.models.blog import Post
    posts_count = db.query(func.count(Post.id)).filter(
        Post.deleted_at.is_(None)
    ).scalar() or 0
    
    # Count open tickets
    open_tickets_count = db.query(func.count(SupportTicket.id)).filter(
        SupportTicket.status == "open"
    ).scalar() or 0
    
    return AdminSimpleDashboardResponse(
        users_count=users_count,
        posts_count=posts_count,
        open_tickets_count=open_tickets_count
    )


@router.get(
    "/dashboard/daily-stats",
    response_model=DailyStatsResponse,
    summary="Admin - Daily System Statistics",
    description="""
    Lấy thống kê hệ thống theo ngày từ bảng daily_system_stats.
    
    **Authorization:** Chỉ admin
    
    **Query Parameters:**
    - days: Số ngày cần lấy (default: 30, max: 365)
    
    **Returns:**
    - Danh sách stats theo ngày (từ mới nhất đến cũ nhất)
    - Mỗi ngày bao gồm: user metrics, volume metrics, community metrics, health metrics
    
    **Use Case:**
    - Vẽ biểu đồ line chart (user growth, active users...)
    - Vẽ biểu đồ bar chart (logs volume, posts...)
    - Phân tích xu hướng tăng trưởng
    """
)
def get_daily_stats(
    days: int = Query(
        30,
        ge=1,
        le=365,
        description="Số ngày cần lấy"
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Lấy daily system statistics
    
    **Security:** Chỉ admin mới có quyền truy cập
    """
    from datetime import date, timedelta
    
    # Lấy daily stats
    items = AdminDashboardService.get_daily_stats(db, days)
    
    # Tính date range
    today = date.today()
    date_from = today - timedelta(days=days - 1)
    
    return DailyStatsResponse(
        items=items,
        total_days=len(items),
        date_from=date_from,
        date_to=today
    )


@router.get(
    "/dashboard/core",
    response_model=CoreDashboardResponse,
    summary="Admin - Core Dashboard (Users, Logs, Retention)",
    description="""
    Lấy core metrics: User stats, Log stats, Retention (DAU/WAU/MAU).
    
    **Authorization:** Chỉ admin
    
    **Query Parameters:**
    - range: 7d (mặc định), 30d, 90d
    
    **Returns:**
    - User Stats: Tổng users, users mới, active users, admin count
    - Log Stats: Tổng food/exercise logs, logs trong range
    - Retention: DAU, WAU, MAU
    """
)
def get_core_dashboard(
    range: str = Query(
        "7d",
        regex="^(7d|30d|90d)$",
        description="Khoảng thời gian: 7d, 30d, 90d"
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Core dashboard metrics"""
    range_map = {"7d": 7, "30d": 30, "90d": 90}
    range_days = range_map[range]
    range_start = datetime.now(timezone.utc) - timedelta(days=range_days)
    
    user_stats = AdminDashboardService.get_user_stats(db, range_days, range_start)
    log_stats = AdminDashboardService.get_log_stats(db, range_start)
    retention_metrics = AdminDashboardService.get_retention_metrics(db)
    
    return CoreDashboardResponse(
        user_stats=user_stats,
        log_stats=log_stats,
        retention_metrics=retention_metrics,
        query_range=range,
        generated_at=datetime.now(timezone.utc)
    )


@router.get(
    "/dashboard/blog",
    response_model=BlogDashboardResponse,
    summary="Admin - Blog Dashboard",
    description="""
    Lấy blog & community metrics.
    
    **Authorization:** Chỉ admin
    
    **Query Parameters:**
    - range: 7d (mặc định), 30d, 90d
    - top_n: Số lượng items trong top lists (default: 10, max: 50)
    
    **Returns:**
    - Total posts, likes, saves
    - Top liked posts
    - Top saved posts
    - Top engagement posts
    - Trending posts (7 ngày gần nhất)
    """
)
def get_blog_dashboard(
    range: str = Query(
        "7d",
        regex="^(7d|30d|90d)$",
        description="Khoảng thời gian: 7d, 30d, 90d"
    ),
    top_n: int = Query(
        10,
        ge=1,
        le=50,
        description="Số lượng items trong top lists"
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Blog dashboard metrics"""
    range_map = {"7d": 7, "30d": 30, "90d": 90}
    range_days = range_map[range]
    range_start = datetime.now(timezone.utc) - timedelta(days=range_days)
    
    blog_stats = AdminDashboardService.get_blog_stats(db, range_start, top_n)
    
    return BlogDashboardResponse(
        blog_stats=blog_stats,
        query_range=range,
        generated_at=datetime.now(timezone.utc)
    )


@router.get(
    "/dashboard/streak",
    response_model=StreakDashboardResponse,
    summary="Admin - Streak Dashboard",
    description="""
    Lấy streak metrics.
    
    **Authorization:** Chỉ admin
    
    **Query Parameters:**
    - range: 7d (mặc định), 30d, 90d (for consistency, not used in logic)
    - top_n: Số lượng users trong top streak list (default: 10, max: 50)
    
    **Returns:**
    - Users with streak > 0
    - Average streak
    - Highest streak + user
    - Top N streak users
    - Users with week/month streak
    """
)
def get_streak_dashboard(
    range: str = Query(
        "7d",
        regex="^(7d|30d|90d)$",
        description="Khoảng thời gian (for consistency)"
    ),
    top_n: int = Query(
        10,
        ge=1,
        le=50,
        description="Số lượng users trong top list"
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Streak dashboard metrics"""
    streak_stats = AdminDashboardService.get_streak_stats(db, top_n)
    
    return StreakDashboardResponse(
        streak_stats=streak_stats,
        query_range=range,
        generated_at=datetime.now(timezone.utc)
    )


@router.post(
    "/dashboard/daily-stats",
    summary="Admin - Calculate & Save Daily Stats (Manual)",
    description="""
    Tính toán và lưu thống kê hệ thống cho 1 ngày cụ thể.
    
    **Authorization:** Chỉ admin
    
    **Query Parameters:**
    - target_date: Ngày cần tính (format: YYYY-MM-DD, default: hôm nay)
    
    **Use Case:**
    - Gọi thủ công để tính toán stats cho một ngày
    - Backfill dữ liệu cho các ngày trước
    - Sửa lại stats nếu có 착ộ
    
    **Chú ý:** Nếu ngày đã có stats thì sẽ UPDATE, chưa có thì INSERT mới
    """
)
def calculate_daily_stats(
    target_date: date = Query(
        default=None,
        description="Ngày cần tính (YYYY-MM-DD). Nếu để trống sẽ lấy hôm nay"
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Manually trigger daily stats calculation
    
    **Security:** Admin only
    **Action:** Calculate và save vào daily_system_stats table
    """
    from datetime import date as date_module
    
    # Nếu không truyền target_date thì lấy hôm nay
    if target_date is None:
        target_date = date_module.today()
    
    try:
        result = AdminDashboardService.calculate_and_save_daily_stats(db, target_date)
        
        return {
            "success": True,
            "message": f"Daily stats {result['action']} for {target_date}",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating stats: {str(e)}"
        )