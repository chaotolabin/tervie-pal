"""
Tạo các utility functions để convert UTC datetime sang local date
và lấy "today" theo local timezone.
"""
from datetime import datetime, date, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo


# Default timezone: Asia/Ho_Chi_Minh (UTC+7)
# TODO: Có thể lấy từ user settings trong tương lai
DEFAULT_TIMEZONE = ZoneInfo('Asia/Ho_Chi_Minh')


def get_local_timezone() -> ZoneInfo:
    """
    Lấy local timezone (hiện tại dùng default, có thể mở rộng để lấy từ user settings)
    
    Returns:
        ZoneInfo: Timezone object
    """
    return DEFAULT_TIMEZONE


def utc_to_local_date(utc_datetime: datetime) -> date:
    """
    Convert UTC datetime sang local date
    
    Args:
        utc_datetime: Datetime với UTC timezone (hoặc naive datetime được coi là UTC)
    
    Returns:
        date: Local date của datetime đó
    
    Example:
        >>> utc_dt = datetime(2025, 1, 1, 23, 0, 0, tzinfo=timezone.utc)  # 23:00 UTC
        >>> utc_to_local_date(utc_dt)  # Returns date(2025, 1, 2) vì 23:00 UTC = 06:00+1 ngày VN
    """
    if utc_datetime.tzinfo is None:
        # Nếu là naive datetime, giả định là UTC
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    elif utc_datetime.tzinfo != timezone.utc:
        # Nếu có timezone khác, convert sang UTC trước
        utc_datetime = utc_datetime.astimezone(timezone.utc)
    
    # Convert sang local timezone
    local_tz = get_local_timezone()
    local_datetime = utc_datetime.astimezone(local_tz)
    
    # Trả về date theo local timezone
    return local_datetime.date()


def get_local_today() -> date:
    """
    Lấy ngày hôm nay theo local timezone (không phải UTC)
    
    Returns:
        date: Ngày hôm nay theo local timezone
    
    Example:
        >>> # Nếu bây giờ là 01:00 UTC ngày 2/1/2025
        >>> # Thì local time là 08:00 ngày 2/1/2025 (UTC+7)
        >>> get_local_today()  # Returns date(2025, 1, 2)
    """
    utc_now = datetime.now(timezone.utc)
    return utc_to_local_date(utc_now)


def local_date_to_utc_range(target_date: date) -> tuple[datetime, datetime]:
    """
    Convert local date sang UTC datetime range (start và end của ngày đó)
    
    Args:
        target_date: Local date cần convert
    
    Returns:
        tuple[datetime, datetime]: (start_dt_utc, end_dt_utc)
            - start_dt_utc: 00:00:00 của target_date theo local timezone, convert sang UTC
            - end_dt_utc: 23:59:59.999999 của target_date theo local timezone, convert sang UTC
    
    Example:
        >>> # target_date = date(2025, 1, 2) (local)
        >>> # Local: 2025-01-02 00:00:00 -> UTC: 2025-01-01 17:00:00 (UTC+7)
        >>> # Local: 2025-01-02 23:59:59 -> UTC: 2025-01-02 16:59:59 (UTC+7)
        >>> start, end = local_date_to_utc_range(date(2025, 1, 2))
    """
    local_tz = get_local_timezone()
    
    # Tạo datetime start và end theo local timezone
    local_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=local_tz)
    local_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=local_tz)
    
    # Convert sang UTC
    start_dt_utc = local_start.astimezone(timezone.utc)
    end_dt_utc = local_end.astimezone(timezone.utc)
    
    return start_dt_utc, end_dt_utc


def datetime_to_local_date(dt: Optional[datetime]) -> Optional[date]:
    """
    Helper function: Convert datetime (có thể None) sang local date
    
    Args:
        dt: Datetime object (có thể None)
    
    Returns:
        date hoặc None
    """
    if dt is None:
        return None
    
    if isinstance(dt, date) and not isinstance(dt, datetime):
        # Nếu đã là date object, trả về luôn
        return dt
    
    return utc_to_local_date(dt)

