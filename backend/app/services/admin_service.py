# """
# Admin Service - Business Logic cho Admin Panel
# Bao gồm: Dashboard Stats, User Management, Blog Management
# """
# from datetime import datetime, timezone, timedelta, date
# from typing import Optional, List, Tuple
# from sqlalchemy.orm import Session
# from sqlalchemy import func, and_, or_, desc, select, case
# from fastapi import HTTPException, status
# import uuid

# from app.models.auth import User, Profile, Goal
# from app.models.log import FoodLogEntry, ExerciseLogEntry
# from app.models.blog import Post, PostLike, PostSave
# from app.models.streak import UserStreakState, StreakDayCache
# from app.models.support import SupportTicket
# from app.schemas.admin import (
#     UserStatsResponse,
#     LogStatsResponse,
#     RetentionMetricsResponse,
#     BlogStatsResponse,
#     StreakStatsResponse,
#     TopPostItem,
#     StreakUserItem,
#     AdminUserListItem,
#     UserActivitySummary,
# )


# class AdminDashboardService:
#     """Service xử lý logic Dashboard Statistics"""
    
#     @staticmethod
#     def get_user_stats(db: Session, range_days: int, range_start: datetime) -> UserStatsResponse:
#         """
#         Thống kê người dùng
        
#         Args:
#             db: Database session
#             range_days: Số ngày cần thống kê
#             range_start: Thời điểm bắt đầu khoảng thời gian
            
#         Returns:
#             UserStatsResponse với các metrics
#         """
#         # Tổng số users
#         total_users = db.query(func.count(User.id)).scalar() or 0
        
#         # Users mới trong khoảng thời gian
#         new_users = db.query(func.count(User.id)).filter(
#             User.created_at >= range_start
#         ).scalar() or 0
        
#         # Active users: có log meal HOẶC log exercise trong range_days
#         active_food = db.query(FoodLogEntry.user_id).filter(
#             FoodLogEntry.logged_at >= range_start,
#             FoodLogEntry.deleted_at.is_(None)
#         ).distinct()
        
#         active_exercise = db.query(ExerciseLogEntry.user_id).filter(
#             ExerciseLogEntry.logged_at >= range_start,
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).distinct()
        
#         # Union 2 queries
#         active_users_subquery = active_food.union(active_exercise).subquery()
#         active_users = db.query(func.count()).select_from(active_users_subquery).scalar() or 0
        
#         # Số admin
#         admin_count = db.query(func.count(User.id)).filter(
#             User.role == "admin"
#         ).scalar() or 0
        
#         return UserStatsResponse(
#             total_users=total_users,
#             new_users=new_users,
#             active_users=active_users,
#             admin_count=admin_count
#         )
    
#     @staticmethod
#     def get_log_stats(db: Session, range_start: datetime) -> LogStatsResponse:
#         """Thống kê logs (food + exercise)"""
#         # Tổng số food logs (all time)
#         total_food = db.query(func.count(FoodLogEntry.id)).filter(
#             FoodLogEntry.deleted_at.is_(None)
#         ).scalar() or 0
        
#         # Tổng số exercise logs (all time)
#         total_exercise = db.query(func.count(ExerciseLogEntry.id)).filter(
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).scalar() or 0
        
#         # Food logs trong range
#         food_in_range = db.query(func.count(FoodLogEntry.id)).filter(
#             FoodLogEntry.logged_at >= range_start,
#             FoodLogEntry.deleted_at.is_(None)
#         ).scalar() or 0
        
#         # Exercise logs trong range
#         exercise_in_range = db.query(func.count(ExerciseLogEntry.id)).filter(
#             ExerciseLogEntry.logged_at >= range_start,
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).scalar() or 0
        
#         return LogStatsResponse(
#             total_food_logs=total_food,
#             total_exercise_logs=total_exercise,
#             food_logs_in_range=food_in_range,
#             exercise_logs_in_range=exercise_in_range
#         )
    
#     @staticmethod
#     def get_retention_metrics(db: Session) -> RetentionMetricsResponse:
#         """
#         Tính retention metrics: DAU, WAU, MAU
#         Dựa trên activity trong FoodLogEntry + ExerciseLogEntry
#         """
#         now = datetime.now(timezone.utc)
        
#         # DAU: 24h
#         dau_start = now - timedelta(days=1)
#         dau_food = db.query(FoodLogEntry.user_id).filter(
#             FoodLogEntry.logged_at >= dau_start,
#             FoodLogEntry.deleted_at.is_(None)
#         ).distinct()
#         dau_exercise = db.query(ExerciseLogEntry.user_id).filter(
#             ExerciseLogEntry.logged_at >= dau_start,
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).distinct()
#         dau = db.query(func.count()).select_from(
#             dau_food.union(dau_exercise).subquery()
#         ).scalar() or 0
        
#         # WAU: 7 days
#         wau_start = now - timedelta(days=7)
#         wau_food = db.query(FoodLogEntry.user_id).filter(
#             FoodLogEntry.logged_at >= wau_start,
#             FoodLogEntry.deleted_at.is_(None)
#         ).distinct()
#         wau_exercise = db.query(ExerciseLogEntry.user_id).filter(
#             ExerciseLogEntry.logged_at >= wau_start,
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).distinct()
#         wau = db.query(func.count()).select_from(
#             wau_food.union(wau_exercise).subquery()
#         ).scalar() or 0
        
#         # MAU: 30 days
#         mau_start = now - timedelta(days=30)
#         mau_food = db.query(FoodLogEntry.user_id).filter(
#             FoodLogEntry.logged_at >= mau_start,
#             FoodLogEntry.deleted_at.is_(None)
#         ).distinct()
#         mau_exercise = db.query(ExerciseLogEntry.user_id).filter(
#             ExerciseLogEntry.logged_at >= mau_start,
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).distinct()
#         mau = db.query(func.count()).select_from(
#             mau_food.union(mau_exercise).subquery()
#         ).scalar() or 0
        
#         return RetentionMetricsResponse(
#             dau=dau,
#             wau=wau,
#             mau=mau
#         )
    
#     @staticmethod
#     def get_blog_stats(db: Session, range_start: datetime, top_n: int = 10) -> BlogStatsResponse:
#         """Thống kê blog + top posts"""
#         # Tổng số posts
#         total_posts = db.query(func.count(Post.id)).filter(
#             Post.deleted_at.is_(None)
#         ).scalar() or 0
        
#         # Posts trong range
#         posts_in_range = db.query(func.count(Post.id)).filter(
#             Post.created_at >= range_start,
#             Post.deleted_at.is_(None)
#         ).scalar() or 0
        
#         # Tổng likes (từ post_likes)
#         total_likes = db.query(func.count(PostLike.post_id)).scalar() or 0
        
#         # Tổng saves
#         total_saves = db.query(func.count(PostSave.post_id)).scalar() or 0
        
#         # Top liked posts
#         top_liked_query = (
#             db.query(
#                 Post,
#                 User.username
#             )
#             .join(User, Post.user_id == User.id)
#             .filter(Post.deleted_at.is_(None))
#             .order_by(desc(Post.like_count))
#             .limit(top_n)
#         )
        
#         top_liked_posts = [
#             TopPostItem(
#                 post_id=post.id,
#                 user_id=post.user_id,
#                 title=post.title,
#                 content_preview=post.content_text[:100] if post.content_text else "",
#                 like_count=post.like_count,
#                 save_count=post.save_count,
#                 total_engagement=post.like_count + post.save_count,
#                 created_at=post.created_at
#             )
#             for post, username in top_liked_query.all()
#         ]
        
#         # Top saved posts
#         top_saved_query = (
#             db.query(Post, User.username)
#             .join(User, Post.user_id == User.id)
#             .filter(Post.deleted_at.is_(None))
#             .order_by(desc(Post.save_count))
#             .limit(top_n)
#         )
        
#         top_saved_posts = [
#             TopPostItem(
#                 post_id=post.id,
#                 user_id=post.user_id,
#                 title=post.title,
#                 content_preview=post.content_text[:100] if post.content_text else "",
#                 like_count=post.like_count,
#                 save_count=post.save_count,
#                 total_engagement=post.like_count + post.save_count,
#                 created_at=post.created_at
#             )
#             for post, username in top_saved_query.all()
#         ]
        
#         # Top engagement (like + save)
#         top_engagement_query = (
#             db.query(Post, User.username)
#             .join(User, Post.user_id == User.id)
#             .filter(Post.deleted_at.is_(None))
#             .order_by(desc(Post.like_count + Post.save_count))
#             .limit(top_n)
#         )
        
#         top_engagement_posts = [
#             TopPostItem(
#                 post_id=post.id,
#                 user_id=post.user_id,
#                 title=post.title,
#                 content_preview=post.content_text[:100] if post.content_text else "",
#                 like_count=post.like_count,
#                 save_count=post.save_count,
#                 total_engagement=post.like_count + post.save_count,
#                 created_at=post.created_at
#             )
#             for post, username in top_engagement_query.all()
#         ]
        
#         # Trending: posts gần đây có engagement cao
#         trending_start = datetime.now(timezone.utc) - timedelta(days=7)
#         trending_query = (
#             db.query(Post, User.username)
#             .join(User, Post.user_id == User.id)
#             .filter(
#                 Post.deleted_at.is_(None),
#                 Post.created_at >= trending_start
#             )
#             .order_by(desc(Post.like_count + Post.save_count))
#             .limit(top_n)
#         )
        
#         trending_posts = [
#             TopPostItem(
#                 post_id=post.id,
#                 user_id=post.user_id,
#                 title=post.title,
#                 content_preview=post.content_text[:100] if post.content_text else "",
#                 like_count=post.like_count,
#                 save_count=post.save_count,
#                 total_engagement=post.like_count + post.save_count,
#                 created_at=post.created_at
#             )
#             for post, username in trending_query.all()
#         ]
        
#         return BlogStatsResponse(
#             total_posts=total_posts,
#             posts_in_range=posts_in_range,
#             total_likes=total_likes,
#             total_saves=total_saves,
#             top_liked_posts=top_liked_posts,
#             top_saved_posts=top_saved_posts,
#             top_engagement_posts=top_engagement_posts,
#             trending_posts=trending_posts
#         )
    
#     @staticmethod
#     def get_streak_stats(db: Session, top_n: int = 10) -> StreakStatsResponse:
#         """Thống kê streak"""
#         # Users có streak > 0
#         users_with_streak = db.query(func.count(UserStreakState.user_id)).filter(
#             UserStreakState.current_streak > 0
#         ).scalar() or 0
        
#         # Streak trung bình
#         avg_streak_result = db.query(func.avg(UserStreakState.current_streak)).filter(
#             UserStreakState.current_streak > 0
#         ).scalar()
#         average_streak = float(avg_streak_result) if avg_streak_result else 0.0
        
#         # Highest streak
#         highest_streak_result = db.query(
#             func.max(UserStreakState.current_streak)
#         ).scalar()
#         highest_streak = highest_streak_result or 0
        
#         # User có highest streak
#         highest_streak_user = None
#         if highest_streak > 0:
#             user_state = db.query(UserStreakState).filter(
#                 UserStreakState.current_streak == highest_streak
#             ).first()
#             if user_state:
#                 highest_streak_user = user_state.user_id
        
#         # Top N users
#         top_streak_query = (
#             db.query(
#                 UserStreakState,
#                 User.username,
#                 User.email
#             )
#             .join(User, UserStreakState.user_id == User.id)
#             .filter(UserStreakState.current_streak > 0)
#             .order_by(desc(UserStreakState.current_streak))
#             .limit(top_n)
#         )
        
#         top_streak_users = [
#             StreakUserItem(
#                 user_id=state.user_id,
#                 username=username,
#                 email=email,
#                 current_streak=state.current_streak,
#                 longest_streak=state.longest_streak
#             )
#             for state, username, email in top_streak_query.all()
#         ]
        
#         # Users có streak >= 7
#         users_week_streak = db.query(func.count(UserStreakState.user_id)).filter(
#             UserStreakState.current_streak >= 7
#         ).scalar() or 0
        
#         # Users có streak >= 30
#         users_month_streak = db.query(func.count(UserStreakState.user_id)).filter(
#             UserStreakState.current_streak >= 30
#         ).scalar() or 0
        
#         return StreakStatsResponse(
#             users_with_streak=users_with_streak,
#             average_streak=average_streak,
#             highest_streak=highest_streak,
#             highest_streak_user_id=highest_streak_user,
#             top_streak_users=top_streak_users,
#             users_with_week_streak=users_week_streak,
#             users_with_month_streak=users_month_streak
#         )


# class AdminUserService:
#     """Service xử lý User Management"""
    
#     @staticmethod
#     def get_users_list(
#         db: Session,
#         page: int = 1,
#         page_size: int = 50,
#         email_filter: Optional[str] = None,
#         role_filter: Optional[str] = None,
#         status_filter: Optional[str] = None
#     ) -> Tuple[List[AdminUserListItem], int]:
#         """
#         Lấy danh sách users với phân trang và filter
        
#         Returns:
#             (list_items, total_count)
#         """
#         query = db.query(
#             User,
#             Profile.full_name,
#             UserStreakState.current_streak
#         ).outerjoin(
#             Profile, User.id == Profile.user_id
#         ).outerjoin(
#             UserStreakState, User.id == UserStreakState.user_id
#         )
        
#         # Filters
#         if email_filter:
#             query = query.filter(User.email.ilike(f"%{email_filter}%"))
        
#         if role_filter:
#             query = query.filter(User.role == role_filter)
        
#         # Count total
#         total = query.count()
        
#         # Pagination
#         offset = (page - 1) * page_size
#         results = query.order_by(desc(User.created_at)).offset(offset).limit(page_size).all()
        
#         # Lấy last_log_at từ logs (tính runtime)
#         items = []
#         for user, full_name, streak in results:
#             # Query last activity
#             last_food = db.query(func.max(FoodLogEntry.logged_at)).filter(
#                 FoodLogEntry.user_id == user.id,
#                 FoodLogEntry.deleted_at.is_(None)
#             ).scalar()
            
#             last_exercise = db.query(func.max(ExerciseLogEntry.logged_at)).filter(
#                 ExerciseLogEntry.user_id == user.id,
#                 ExerciseLogEntry.deleted_at.is_(None)
#             ).scalar()
            
#             last_log = None
#             if last_food and last_exercise:
#                 last_log = max(last_food, last_exercise)
#             elif last_food:
#                 last_log = last_food
#             elif last_exercise:
#                 last_log = last_exercise
            
#             items.append(AdminUserListItem(
#                 id=user.id,
#                 username=user.username,
#                 email=user.email,
#                 role=user.role,
#                 full_name=full_name,
#                 created_at=user.created_at,
#                 current_streak=streak or 0,
#                 last_log_at=last_log
#             ))
        
#         return items, total
    
#     @staticmethod
#     def get_user_detail(db: Session, user_id: uuid.UUID) -> dict:
#         """Lấy chi tiết user kèm activity summary"""
#         user = db.query(User).filter(User.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         profile = db.query(Profile).filter(Profile.user_id == user_id).first()
#         goal = db.query(Goal).filter(Goal.user_id == user_id).first()
#         streak_state = db.query(UserStreakState).filter(UserStreakState.user_id == user_id).first()
        
#         # Activity summary
#         total_food = db.query(func.count(FoodLogEntry.id)).filter(
#             FoodLogEntry.user_id == user_id,
#             FoodLogEntry.deleted_at.is_(None)
#         ).scalar() or 0
        
#         total_exercise = db.query(func.count(ExerciseLogEntry.id)).filter(
#             ExerciseLogEntry.user_id == user_id,
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).scalar() or 0
        
#         total_posts = db.query(func.count(Post.id)).filter(
#             Post.user_id == user_id,
#             Post.deleted_at.is_(None)
#         ).scalar() or 0
        
#         last_food = db.query(func.max(FoodLogEntry.logged_at)).filter(
#             FoodLogEntry.user_id == user_id,
#             FoodLogEntry.deleted_at.is_(None)
#         ).scalar()
        
#         last_exercise = db.query(func.max(ExerciseLogEntry.logged_at)).filter(
#             ExerciseLogEntry.user_id == user_id,
#             ExerciseLogEntry.deleted_at.is_(None)
#         ).scalar()
        
#         last_post = db.query(func.max(Post.created_at)).filter(
#             Post.user_id == user_id,
#             Post.deleted_at.is_(None)
#         ).scalar()
        
#         activity = UserActivitySummary(
#             total_food_logs=total_food,
#             total_exercise_logs=total_exercise,
#             total_posts=total_posts,
#             last_food_log_at=last_food,
#             last_exercise_log_at=last_exercise,
#             last_post_at=last_post
#         )
        
#         return {
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "role": user.role,
#             "created_at": user.created_at,
#             "updated_at": user.updated_at,
#             "full_name": profile.full_name if profile else None,
#             "gender": profile.gender if profile else None,
#             "date_of_birth": profile.date_of_birth if profile else None,
#             "height_cm_default": profile.height_cm_default if profile else None,
#             "password_changed_at": user.password_changed_at,
#             "current_streak": streak_state.current_streak if streak_state else 0,
#             "longest_streak": streak_state.longest_streak if streak_state else 0,
#             "last_on_time_day": streak_state.last_on_time_day if streak_state else None,
#             "activity_summary": activity,
#             "goal_type": goal.goal_type if goal else None,
#             "daily_calorie_target": goal.daily_calorie_target if goal else None
#         }
    
#     @staticmethod
#     def update_user_role(db: Session, user_id: uuid.UUID, new_role: str, admin_id: uuid.UUID) -> User:
#         """Cập nhật role của user"""
#         user = db.query(User).filter(User.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         # Không cho phép admin tự thay đổi role của chính mình
#         if user_id == admin_id:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Cannot change your own role"
#             )
        
#         user.role = new_role
#         user.updated_at = datetime.now(timezone.utc)
#         db.commit()
#         db.refresh(user)
        
#         return user
    
#     @staticmethod
#     def adjust_user_streak(
#         db: Session,
#         user_id: uuid.UUID,
#         new_streak: int,
#         reason: str,
#         admin_id: uuid.UUID
#     ) -> UserStreakState:
#         """Điều chỉnh streak của user (xử lý khiếu nại)"""
#         streak_state = db.query(UserStreakState).filter(
#             UserStreakState.user_id == user_id
#         ).first()
        
#         if not streak_state:
#             # Tạo mới nếu chưa có
#             streak_state = UserStreakState(
#                 user_id=user_id,
#                 current_streak=new_streak,
#                 longest_streak=new_streak,
#                 updated_at=datetime.now(timezone.utc)
#             )
#             db.add(streak_state)
#         else:
#             streak_state.current_streak = new_streak
#             if new_streak > streak_state.longest_streak:
#                 streak_state.longest_streak = new_streak
#             streak_state.updated_at = datetime.now(timezone.utc)
        
#         # TODO: Log action vào audit table nếu cần
#         # AdminAuditLog(admin_id=admin_id, action="adjust_streak", reason=reason, ...)
        
#         db.commit()
#         db.refresh(streak_state)
        
#         return streak_state


# class AdminBlogService:
#     """Service xử lý Blog Management"""
    
#     @staticmethod
#     def get_posts_list(
#         db: Session,
#         page: int = 1,
#         page_size: int = 50,
#         include_deleted: bool = False
#     ) -> Tuple[List[dict], int]:
#         """Lấy danh sách posts (admin view)"""
#         query = db.query(
#             Post,
#             User.username
#         ).join(User, Post.user_id == User.id)
        
#         if not include_deleted:
#             query = query.filter(Post.deleted_at.is_(None))
        
#         total = query.count()
        
#         offset = (page - 1) * page_size
#         results = query.order_by(desc(Post.created_at)).offset(offset).limit(page_size).all()
        
#         items = []
#         for post, username in results:
#             items.append({
#                 "id": post.id,
#                 "user_id": post.user_id,
#                 "username": username,
#                 "title": post.title,
#                 "content_preview": post.content_text[:100] if post.content_text else "",
#                 "like_count": post.like_count,
#                 "save_count": post.save_count,
#                 "created_at": post.created_at,
#                 "deleted_at": post.deleted_at
#             })
        
#         return items, total
    
#     @staticmethod
#     def delete_post(
#         db: Session,
#         post_id: int,
#         reason: Optional[str],
#         admin_id: uuid.UUID
#     ) -> Post:
#         """Soft delete post"""
#         post = db.query(Post).filter(Post.id == post_id).first()
#         if not post:
#             raise HTTPException(status_code=404, detail="Post not found")
        
#         if post.deleted_at:
#             raise HTTPException(status_code=400, detail="Post already deleted")
        
#         post.deleted_at = datetime.now(timezone.utc)
#         post.updated_at = datetime.now(timezone.utc)
        
#         # TODO: Log action
        
#         db.commit()
#         db.refresh(post)
        
#         return post
