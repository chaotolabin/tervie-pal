"""
Admin Service - Business Logic cho Admin Panel
Bao gồm: Dashboard Stats, User Management, Blog Management
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case

from app.models.auth import User
from app.models.log import FoodLogEntry, ExerciseLogEntry
from app.models.blog import Post, PostLike, PostSave
from app.models.streak import UserStreakState
from app.schemas.admin import (
    UserStatsResponse,
    LogStatsResponse,
    RetentionMetricsResponse,
    BlogStatsResponse,
    StreakStatsResponse,
    TopPostItem,
    StreakUserItem,
)


class AdminDashboardService:
    """Service xử lý logic Dashboard Statistics"""
    
    @staticmethod
    def get_user_stats(db: Session, range_days: int, range_start: datetime) -> UserStatsResponse:
        """
        Thống kê người dùng
        
        Args:
            db: Database session
            range_days: Số ngày cần thống kê
            range_start: Thời điểm bắt đầu khoảng thời gian
            
        Returns:
            UserStatsResponse với các metrics
        """
        # Tổng số users
        total_users = db.query(func.count(User.id)).scalar() or 0
        
        # Users mới trong khoảng thời gian
        new_users = db.query(func.count(User.id)).filter(
            User.created_at >= range_start
        ).scalar() or 0
        
        # Active users: có log meal HOẶC log exercise trong range_days
        active_food = db.query(FoodLogEntry.user_id).filter(
            FoodLogEntry.logged_at >= range_start,
            FoodLogEntry.deleted_at.is_(None)
        ).distinct()
        
        active_exercise = db.query(ExerciseLogEntry.user_id).filter(
            ExerciseLogEntry.logged_at >= range_start,
            ExerciseLogEntry.deleted_at.is_(None)
        ).distinct()
        
        # Union 2 queries
        active_users_subquery = active_food.union(active_exercise).subquery()
        active_users = db.query(func.count()).select_from(active_users_subquery).scalar() or 0
        
        # Số admin
        admin_count = db.query(func.count(User.id)).filter(
            User.role == "admin"
        ).scalar() or 0
        
        return UserStatsResponse(
            total_users=total_users,
            new_users=new_users,
            active_users=active_users,
            admin_count=admin_count
        )
    
    @staticmethod
    def get_log_stats(db: Session, range_start: datetime) -> LogStatsResponse:
        """Thống kê logs (food + exercise)"""
        # Tổng số food logs (all time)
        total_food = db.query(func.count(FoodLogEntry.id)).filter(
            FoodLogEntry.deleted_at.is_(None)
        ).scalar() or 0
        
        # Tổng số exercise logs (all time)
        total_exercise = db.query(func.count(ExerciseLogEntry.id)).filter(
            ExerciseLogEntry.deleted_at.is_(None)
        ).scalar() or 0
        
        # Food logs trong range
        food_in_range = db.query(func.count(FoodLogEntry.id)).filter(
            FoodLogEntry.logged_at >= range_start,
            FoodLogEntry.deleted_at.is_(None)
        ).scalar() or 0
        
        # Exercise logs trong range
        exercise_in_range = db.query(func.count(ExerciseLogEntry.id)).filter(
            ExerciseLogEntry.logged_at >= range_start,
            ExerciseLogEntry.deleted_at.is_(None)
        ).scalar() or 0
        
        return LogStatsResponse(
            total_food_logs=total_food,
            total_exercise_logs=total_exercise,
            food_logs_in_range=food_in_range,
            exercise_logs_in_range=exercise_in_range
        )

    @staticmethod
    def _count_active_users(db: Session, start_time: datetime) -> int:
        """
        Đếm số user active duy nhất (unique) kể từ thời điểm start_time
        dựa trên Food Log và Exercise Log.
        """
        # Query users từ Food Log
        last_log_food = case(
            (FoodLogEntry.updated_at.is_not(None), FoodLogEntry.updated_at),
            else_=FoodLogEntry.created_at
        )
        active_food = db.query(FoodLogEntry.user_id).filter(
            last_log_food >= start_time,
            FoodLogEntry.deleted_at.is_(None)
        ).distinct()
        
        # Query users từ Exercise Log
        last_log_exercise = case(
            (ExerciseLogEntry.updated_at.is_not(None), ExerciseLogEntry.updated_at),
            else_=ExerciseLogEntry.created_at
        )
        active_exercise = db.query(ExerciseLogEntry.user_id).filter(
            last_log_exercise >= start_time,
            ExerciseLogEntry.deleted_at.is_(None)
        ).distinct()
        
        # Union 2 tập hợp lại để loại bỏ trùng lặp giữa 2 bảng
        # (VD: User vừa ăn vừa tập thì chỉ tính là 1 active user)
        active_users_subquery = active_food.union(active_exercise).subquery()
        
        # Đếm tổng
        count = db.query(func.count()).select_from(active_users_subquery).scalar()
        
        return count or 0

    @staticmethod
    def get_retention_metrics(db: Session) -> RetentionMetricsResponse:
        """
        Tính retention metrics: DAU, WAU, MAU
        Dựa trên activity trong FoodLogEntry + ExerciseLogEntry
        """
        now = datetime.now(timezone.utc)
        
        # DAU: 24h
        dau = AdminDashboardService._count_active_users(db, start_time=now - timedelta(days=1))
        
        # WAU: 7 days
        wau = AdminDashboardService._count_active_users(db, start_time=now - timedelta(days=7))
        
        # MAU: 30 days
        mau = AdminDashboardService._count_active_users(db, start_time=now - timedelta(days=30))
        
        return RetentionMetricsResponse(
            dau=dau,
            wau=wau,
            mau=mau
        )
    
    @staticmethod
    def get_blog_stats(db: Session, range_start: datetime, top_n: int = 10) -> BlogStatsResponse:
        """Thống kê blog + top posts"""
        # Tổng số posts
        total_posts = db.query(func.count(Post.id)).filter(
            Post.deleted_at.is_(None)
        ).scalar() or 0
        
        # Posts trong range
        posts_in_range = db.query(func.count(Post.id)).filter(
            Post.created_at >= range_start,
            Post.deleted_at.is_(None)
        ).scalar() or 0
        
        # Tổng likes (từ post_likes)
        total_likes = db.query(func.count(PostLike.post_id)).scalar() or 0
        
        # Tổng saves
        total_saves = db.query(func.count(PostSave.post_id)).scalar() or 0
        
        # Top liked posts
        top_liked_query = (
            db.query(
                Post,
                User.username
            )
            .join(User, Post.user_id == User.id)
            .filter(Post.deleted_at.is_(None))
            .order_by(desc(Post.like_count))
            .limit(top_n)
        )
        
        top_liked_posts = [
            TopPostItem(
                post_id=post.id,
                user_id=post.user_id,
                title=post.title,
                content_preview=post.content_text[:100] if post.content_text else "",
                like_count=post.like_count,
                save_count=post.save_count,
                total_engagement=post.like_count + post.save_count,
                created_at=post.created_at
            )
            for post, username in top_liked_query.all()
        ]
        
        # Top saved posts
        top_saved_query = (
            db.query(Post, User.username)
            .join(User, Post.user_id == User.id)
            .filter(Post.deleted_at.is_(None))
            .order_by(desc(Post.save_count))
            .limit(top_n)
        )
        
        top_saved_posts = [
            TopPostItem(
                post_id=post.id,
                user_id=post.user_id,
                title=post.title,
                content_preview=post.content_text[:100] if post.content_text else "",
                like_count=post.like_count,
                save_count=post.save_count,
                total_engagement=post.like_count + post.save_count,
                created_at=post.created_at
            )
            for post, username in top_saved_query.all()
        ]
        
        # Top engagement (like + save)
        top_engagement_query = (
            db.query(Post, User.username)
            .join(User, Post.user_id == User.id)
            .filter(Post.deleted_at.is_(None))
            .order_by(desc(Post.like_count + Post.save_count))
            .limit(top_n)
        )
        
        top_engagement_posts = [
            TopPostItem(
                post_id=post.id,
                user_id=post.user_id,
                title=post.title,
                content_preview=post.content_text[:100] if post.content_text else "",
                like_count=post.like_count,
                save_count=post.save_count,
                total_engagement=post.like_count + post.save_count,
                created_at=post.created_at
            )
            for post, username in top_engagement_query.all()
        ]
        
        # Trending: posts gần đây có engagement cao
        trending_start = datetime.now(timezone.utc) - timedelta(days=7)
        trending_query = (
            db.query(Post, User.username)
            .join(User, Post.user_id == User.id)
            .filter(
                Post.deleted_at.is_(None),
                Post.created_at >= trending_start
            )
            .order_by(desc(Post.like_count + Post.save_count))
            .limit(top_n)
        )
        
        trending_posts = [
            TopPostItem(
                post_id=post.id,
                user_id=post.user_id,
                title=post.title,
                content_preview=post.content_text[:100] if post.content_text else "",
                like_count=post.like_count,
                save_count=post.save_count,
                total_engagement=post.like_count + post.save_count,
                created_at=post.created_at
            )
            for post, username in trending_query.all()
        ]
        
        return BlogStatsResponse(
            total_posts=total_posts,
            posts_in_range=posts_in_range,
            total_likes=total_likes,
            total_saves=total_saves,
            top_liked_posts=top_liked_posts,
            top_saved_posts=top_saved_posts,
            top_engagement_posts=top_engagement_posts,
            trending_posts=trending_posts
        )
    
    @staticmethod
    def get_streak_stats(db: Session, top_n: int = 10) -> StreakStatsResponse:
        """Thống kê streak"""
        # Users có streak > 0
        users_with_streak = db.query(func.count(UserStreakState.user_id)).filter(
            UserStreakState.current_streak > 0
        ).scalar() or 0
        
        # Streak trung bình
        avg_streak_result = db.query(func.avg(UserStreakState.current_streak)).filter(
            UserStreakState.current_streak > 0
        ).scalar()
        average_streak = float(avg_streak_result) if avg_streak_result else 0.0
        
        # Highest streak
        highest_streak_result = db.query(
            func.max(UserStreakState.current_streak)
        ).scalar()
        highest_streak = highest_streak_result or 0
        
        # User có highest streak
        highest_streak_user = None
        if highest_streak > 0:
            user_state = db.query(UserStreakState).filter(
                UserStreakState.current_streak == highest_streak
            ).first()
            if user_state:
                highest_streak_user = user_state.user_id
        
        # Top N users
        top_streak_query = (
            db.query(
                UserStreakState,
                User.username,
                User.email
            )
            .join(User, UserStreakState.user_id == User.id)
            .filter(UserStreakState.current_streak > 0)
            .order_by(desc(UserStreakState.current_streak))
            .limit(top_n)
        )
        
        top_streak_users = [
            StreakUserItem(
                user_id=state.user_id,
                username=username,
                email=email,
                current_streak=state.current_streak,
                longest_streak=state.longest_streak
            )
            for state, username, email in top_streak_query.all()
        ]
        
        # Users có streak >= 7
        users_week_streak = db.query(func.count(UserStreakState.user_id)).filter(
            UserStreakState.current_streak >= 7
        ).scalar() or 0
        
        # Users có streak >= 30
        users_month_streak = db.query(func.count(UserStreakState.user_id)).filter(
            UserStreakState.current_streak >= 30
        ).scalar() or 0
        
        return StreakStatsResponse(
            users_with_streak=users_with_streak,
            average_streak=average_streak,
            highest_streak=highest_streak,
            highest_streak_user_id=highest_streak_user,
            top_streak_users=top_streak_users,
            users_with_week_streak=users_week_streak,
            users_with_month_streak=users_month_streak
        )