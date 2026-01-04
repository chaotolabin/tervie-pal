"""
API Routes cho Admin Dashboard (Statistics)
Endpoint: GET /admin/dashboard/stats
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.auth import User
from app.models.support import SupportTicket
from app.schemas.admin import (
    AdminDashboardStatsResponse,
    AdminSimpleDashboardResponse
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
