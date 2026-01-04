"""
Service layer cho Streak logic - OPTIMIZED VERSION
Tính toán streak từ logs (foods/exercises) với caching hiệu quả
"""
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, exists, literal

from app.models.streak import StreakDayCache, UserStreakState, StreakStatus
from app.models.log import FoodLogEntry, ExerciseLogEntry
from app.schemas.streak import StreakDayResponse, StreakResponse, StreakWeekResponse
from app.utils.timezone import get_local_today, local_date_to_utc_range


class StreakService:
    """
    Service để tính toán và quản lý streak - OPTIMIZED
    
    Chiến lược tối ưu:
    1. Đọc streak state trực tiếp từ user_streak_state (đã được cache)
    2. Query batch 7 ngày một lần từ streak_days_cache  
    3. Chỉ tính toán lazy cho ngày hôm nay (nếu chưa cache)
    4. Update streak state chỉ khi có log mới (không phải mỗi lần đọc)
    """

    # ==================== BATCH QUERY METHODS (OPTIMIZED) ====================
    
    @staticmethod
    def _get_cached_days_batch(
        db: Session, 
        user_id: uuid.UUID, 
        start_day: date, 
        end_day: date
    ) -> Dict[date, StreakStatus]:
        """
        Query batch: Lấy tất cả cached days trong khoảng [start_day, end_day]
        Returns: Dict[date, StreakStatus] để tra cứu O(1)
        """
        cached_rows = db.query(StreakDayCache.day, StreakDayCache.status).filter(
            and_(
                StreakDayCache.user_id == user_id,
                StreakDayCache.day >= start_day,
                StreakDayCache.day <= end_day
            )
        ).all()
        
        return {row.day: row.status for row in cached_rows}

    @staticmethod
    def _check_today_completion(db: Session, user_id: uuid.UUID) -> bool:
        """
        Kiểm tra nhanh: hôm nay có ít nhất 1 food log HOẶC 1 exercise log không?
        Sử dụng EXISTS subquery thay vì COUNT để tối ưu performance
        """
        today = get_local_today()
        return StreakService._check_date_completion(db, user_id, today)
    
    @staticmethod
    def _check_date_completion(db: Session, user_id: uuid.UUID, target_date: date) -> bool:
        """
        Kiểm tra nhanh: một ngày cụ thể có ít nhất 1 food log HOẶC 1 exercise log không?
        Sử dụng EXISTS subquery thay vì COUNT để tối ưu performance
        
        Logic: Chỉ cần có food log HOẶC exercise log là hoàn thành rồi.
        
        Args:
            db: Database session
            user_id: UUID của user
            target_date: Ngày cần kiểm tra (local date)
        
        Returns:
            bool: True nếu đã có ít nhất 1 food log hoặc 1 exercise log trong ngày đó
        """
        # Convert local date sang UTC datetime range
        start_dt, end_dt = local_date_to_utc_range(target_date)
        
        # EXISTS query nhanh hơn COUNT khi chỉ cần biết có/không
        # Sử dụng range comparison thay vì func.date() để đảm bảo đúng timezone
        has_food = db.query(
            exists().where(
                and_(
                    FoodLogEntry.user_id == user_id,
                    FoodLogEntry.logged_at >= start_dt,
                    FoodLogEntry.logged_at <= end_dt,
                    FoodLogEntry.deleted_at.is_(None)
                )
            )
        ).scalar()
        
        has_exercise = db.query(
            exists().where(
                and_(
                    ExerciseLogEntry.user_id == user_id,
                    ExerciseLogEntry.logged_at >= start_dt,
                    ExerciseLogEntry.logged_at <= end_dt,
                    ExerciseLogEntry.deleted_at.is_(None)
                )
            )
        ).scalar()
        
        # Chỉ cần có food HOẶC exercise là hoàn thành
        return has_food or has_exercise

    @staticmethod
    def _get_week_statuses(
        db: Session, 
        user_id: uuid.UUID, 
        end_day: date
    ) -> List[StreakDayResponse]:
        """
        Lấy status của 7 ngày (end_day - 6 đến end_day) - OPTIMIZED
        
        Chiến lược:
        1. Query batch tất cả cached days trong 7 ngày
        2. Với ngày hôm nay: check logs nếu chưa cache
        3. Với ngày quá khứ: check logs nếu chưa cache (có thể là YELLOW nếu có log)
        """
        today = get_local_today()
        start_day = end_day - timedelta(days=6)
        
        # 1. Query batch cached days
        cached_dict = StreakService._get_cached_days_batch(db, user_id, start_day, end_day)
        
        # 2. Build response
        week_days = []
        for i in range(7):
            target_day = start_day + timedelta(days=i)
            
            if target_day in cached_dict:
                # Đã cache => dùng cache
                status = cached_dict[target_day]
            elif target_day == today:
                # Hôm nay chưa cache => check logs
                if StreakService._check_today_completion(db, user_id):
                    status = StreakStatus.GREEN
                else:
                    status = StreakStatus.NONE
            elif target_day > today:
                # Tương lai => NONE
                status = StreakStatus.NONE
            else:
                # Quá khứ chưa cache => check logs
                # Nếu có log thì là YELLOW, không có thì NONE
                if StreakService._check_date_completion(db, user_id, target_day):
                    status = StreakStatus.YELLOW
                else:
                    status = StreakStatus.NONE
            
            week_days.append(StreakDayResponse(day=target_day, status=status))
        
        return week_days

    # ==================== MAIN API METHODS ====================

    @staticmethod
    def get_streak(db: Session, user_id: uuid.UUID) -> StreakResponse:
        """
        GET /streak - Lấy chuỗi hiện tại + 7 ngày gần nhất
        
        OPTIMIZED: Không tính lại streak mỗi lần, chỉ đọc từ cache
        - current_streak và longest_streak từ user_streak_state
        - 7 ngày từ streak_days_cache (batch query)
        
        Complexity: O(1) database round-trips (2-3 queries max)
        """
        today = get_local_today()
        
        # 1. Lấy streak state từ cache (không tính lại!)
        streak_state = db.query(UserStreakState).filter(
            UserStreakState.user_id == user_id
        ).first()
        
        # Nếu chưa có state => user mới, tạo mới với giá trị 0
        if not streak_state:
            streak_state = UserStreakState(
                user_id=user_id,
                current_streak=0,
                longest_streak=0,
                last_on_time_day=None
            )
            db.add(streak_state)
            db.commit()
        
        # 2. Lấy 7 ngày gần nhất (batch query)
        week_days = StreakService._get_week_statuses(db, user_id, today)
        
        # 3. Tính current_streak realtime cho accurate (dựa vào cache + hôm nay)
        #    Điều này đảm bảo nếu user vừa log xong, streak được cập nhật ngay
        current_streak = StreakService._calculate_current_streak_fast(db, user_id, streak_state)
        
        return StreakResponse(
            current_streak=current_streak,
            longest_streak=streak_state.longest_streak,
            week=week_days
        )

    @staticmethod
    def _calculate_current_streak_fast(
        db: Session, 
        user_id: uuid.UUID, 
        streak_state: UserStreakState
    ) -> int:
        """
        Tính current_streak nhanh dựa vào last_on_time_day + check hôm nay
        
        Logic:
        - Nếu last_on_time_day = hôm nay => streak đang active
        - Nếu last_on_time_day = hôm qua => check hôm nay xem có tiếp tục không
        - Nếu last_on_time_day < hôm qua - 1 => streak đã reset
        """
        today = get_local_today()
        yesterday = today - timedelta(days=1)
        
        # Nếu chưa có last_on_time_day => streak = 0
        if not streak_state.last_on_time_day:
            # Check nếu hôm nay hoàn thành => streak = 1
            if StreakService._check_today_completion(db, user_id):
                return 1
            return 0
        
        last_day = streak_state.last_on_time_day
        stored_streak = streak_state.current_streak
        
        if last_day == today:
            # Đã hoàn thành hôm nay => trả về streak hiện tại
            return stored_streak
        elif last_day == yesterday:
            # Hôm qua hoàn thành => check hôm nay
            if StreakService._check_today_completion(db, user_id):
                return stored_streak + 1
            else:
                # Hôm nay chưa hoàn thành nhưng streak vẫn tính (còn trong deadline)
                return stored_streak
        else:
            # last_day < yesterday => streak đã bị break
            # Check nếu hôm nay có hoàn thành => streak mới = 1
            if StreakService._check_today_completion(db, user_id):
                return 1
            return 0

    @staticmethod
    def get_streak_week(
        db: Session, 
        user_id: uuid.UUID, 
        end_day: Optional[date] = None
    ) -> StreakWeekResponse:
        """
        GET /streak/week - Lấy cửa sổ 7 ngày tuỳ chọn
        
        OPTIMIZED: Batch query thay vì 7 queries riêng lẻ
        """
        if end_day is None:
            end_day = get_local_today()
        
        week_days = StreakService._get_week_statuses(db, user_id, end_day)
        
        return StreakWeekResponse(
            end_day=end_day,
            week=week_days
        )

    # ==================== UPDATE METHODS (called when logging) ====================

    @staticmethod
    def update_streak_on_log(db: Session, user_id: uuid.UUID, log_date: date):
        """
        Cập nhật streak khi user tạo log mới
        
        Được gọi từ Food/Exercise log services khi user log thành công.
        Đây là nơi DUY NHẤT streak được tính lại (write-through cache).
        
        Logic:
        - Chỉ cộng streak một lần mỗi ngày. Nếu ngày đó đã có cache (GREEN hoặc YELLOW),
          thì không cộng nữa.
        - Nếu log ngày hôm nay và hoàn thành → set GREEN
        - Nếu log ngày quá khứ và hoàn thành → set YELLOW
        - Chỉ cộng streak state khi log ngày hôm nay (GREEN)
        """
        today = get_local_today()
        
        # Không xử lý log ngày tương lai
        if log_date > today:
            return
        
        # Check xem ngày đó đã có cache chưa (đã cộng streak rồi)
        existing_cache = db.query(StreakDayCache).filter(
            and_(
                StreakDayCache.user_id == user_id,
                StreakDayCache.day == log_date
            )
        ).first()
        
        # Nếu đã có cache rồi (GREEN hoặc YELLOW), không cộng nữa
        if existing_cache:
            return
        
        # Check nếu ngày đó đã hoàn thành (có food log HOẶC exercise log)
        if not StreakService._check_date_completion(db, user_id, log_date):
            return
        
        # Xác định status dựa trên ngày log
        if log_date == today:
            # Log hôm nay → GREEN và cộng streak
            StreakService._cache_day_and_update_streak(db, user_id, log_date, StreakStatus.GREEN)
        else:
            # Log ngày quá khứ → YELLOW, không cộng streak state
            # Chỉ cache status, không update streak state
            cache_entry = StreakDayCache(
                user_id=user_id,
                day=log_date,
                status=StreakStatus.YELLOW
            )
            db.add(cache_entry)
            db.commit()

    @staticmethod
    def _cache_day_and_update_streak(
        db: Session, 
        user_id: uuid.UUID, 
        target_day: date, 
        status: StreakStatus
    ):
        """
        Cache ngày và cập nhật streak state atomically
        """
        # 1. Upsert vào streak_days_cache
        existing_cache = db.query(StreakDayCache).filter(
            and_(
                StreakDayCache.user_id == user_id,
                StreakDayCache.day == target_day
            )
        ).first()
        
        if not existing_cache:
            cache_entry = StreakDayCache(
                user_id=user_id,
                day=target_day,
                status=status
            )
            db.add(cache_entry)
        else:
            existing_cache.status = status
            existing_cache.updated_at = datetime.now(timezone.utc)
        
        # 2. Update user_streak_state
        streak_state = db.query(UserStreakState).filter(
            UserStreakState.user_id == user_id
        ).first()
        
        if not streak_state:
            streak_state = UserStreakState(
                user_id=user_id,
                current_streak=1,
                longest_streak=1,
                last_on_time_day=target_day
            )
            db.add(streak_state)
        else:
            yesterday = target_day - timedelta(days=1)
            
            if streak_state.last_on_time_day == yesterday:
                # Tiếp tục streak
                streak_state.current_streak += 1
            elif streak_state.last_on_time_day == target_day:
                # Đã cache rồi, không làm gì
                pass
            else:
                # Streak bị break, reset về 1
                streak_state.current_streak = 1
            
            # Update longest nếu cần
            if streak_state.current_streak > streak_state.longest_streak:
                streak_state.longest_streak = streak_state.current_streak
            
            streak_state.last_on_time_day = target_day
            streak_state.updated_at = datetime.now(timezone.utc)
        
        db.commit()

    # ==================== LEGACY METHODS (kept for compatibility) ====================

    @staticmethod
    def get_today_status(db: Session, user_id: uuid.UUID) -> StreakStatus:
        """
        Tính status của hôm nay (green/yellow/none) - LEGACY
        Giữ lại cho backward compatibility
        """
        today = get_local_today()
        
        # Check cache trước
        cached = db.query(StreakDayCache).filter(
            and_(
                StreakDayCache.user_id == user_id,
                StreakDayCache.day == today
            )
        ).first()
        
        if cached:
            return cached.status
        
        # Check logs
        if StreakService._check_today_completion(db, user_id):
            return StreakStatus.GREEN
        
        return StreakStatus.NONE

    @staticmethod
    def get_day_status(db: Session, user_id: uuid.UUID, target_day: date) -> StreakStatus:
        """
        Lấy status của một ngày cụ thể - LEGACY
        Giữ lại cho backward compatibility
        """
        today = get_local_today()
        
        # Check cache
        cached = db.query(StreakDayCache).filter(
            and_(
                StreakDayCache.user_id == user_id,
                StreakDayCache.day == target_day
            )
        ).first()
        
        if cached:
            return cached.status
        
        # Hôm nay => check logs
        if target_day == today:
            if StreakService._check_today_completion(db, user_id):
                return StreakStatus.GREEN
            return StreakStatus.NONE
        
        # Quá khứ không cache => NONE
        return StreakStatus.NONE

    @staticmethod
    def calculate_streak(db: Session, user_id: uuid.UUID) -> Tuple[int, int]:
        """
        Tính current_streak và longest_streak - LEGACY
        Giữ lại cho admin tools hoặc batch jobs
        
        ⚠️ KHÔNG nên gọi method này trong API hot path
        """
        today = get_local_today()
        
        # Query batch cached days
        cached_days = db.query(StreakDayCache).filter(
            StreakDayCache.user_id == user_id
        ).order_by(StreakDayCache.day.desc()).all()
        
        cached_dict = {day.day: day.status for day in cached_days}
        
        # Check hôm nay
        if today not in cached_dict:
            if StreakService._check_today_completion(db, user_id):
                cached_dict[today] = StreakStatus.GREEN
        
        # Tính streak từ hôm nay quay lại
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        current_date = today
        max_days = 365  # Giới hạn
        
        for i in range(max_days):
            status = cached_dict.get(current_date, StreakStatus.NONE)
            
            if status == StreakStatus.GREEN:
                temp_streak += 1
            else:
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                if i == 0 or (i == 1 and current_streak == 0):
                    current_streak = temp_streak
                temp_streak = 0
            
            current_date -= timedelta(days=1)
        
        # Final check
        if temp_streak > longest_streak:
            longest_streak = temp_streak
        if current_streak == 0:
            current_streak = temp_streak
        
        return current_streak, longest_streak

    @staticmethod
    def update_user_streak_state(db: Session, user_id: uuid.UUID):
        """
        Cập nhật bảng user_streak_state - LEGACY
        Giữ lại cho admin batch jobs
        """
        current_streak, longest_streak = StreakService.calculate_streak(db, user_id)
        today = get_local_today()
        
        streak_state = db.query(UserStreakState).filter(
            UserStreakState.user_id == user_id
        ).first()
        
        if not streak_state:
            streak_state = UserStreakState(
                user_id=user_id,
                current_streak=current_streak,
                longest_streak=longest_streak,
                last_on_time_day=today if current_streak > 0 else None
            )
            db.add(streak_state)
        else:
            streak_state.current_streak = current_streak
            streak_state.longest_streak = longest_streak
            if current_streak > 0:
                streak_state.last_on_time_day = today
            streak_state.updated_at = datetime.now(timezone.utc)
        
        db.commit()
