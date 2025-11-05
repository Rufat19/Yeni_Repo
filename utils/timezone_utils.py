"""
Bakı vaxtı (GMT+4) ilə işləmək üçün utility funksiyalar
"""
from datetime import datetime, timezone, timedelta

# Bakı vaxtı zone (GMT+4)
BAKU_TIMEZONE = timezone(timedelta(hours=4))

def get_baku_time():
    """Bakı vaxtını qaytarır"""
    return datetime.now(BAKU_TIMEZONE)

def get_baku_time_str(format_str="%Y-%m-%d %H:%M:%S"):
    """Bakı vaxtını string olaraq qaytarır"""
    return get_baku_time().strftime(format_str)

def get_baku_time_short():
    """Qısa Bakı vaxtını qaytarır (HH:MM:SS)"""
    return get_baku_time_str("%H:%M:%S")

def get_baku_date():
    """Bakı vaxtı ilə tarixi qaytarır (YYYY-MM-DD)"""
    return get_baku_time_str("%Y-%m-%d")

def utc_to_baku(utc_dt):
    """UTC vaxtını Bakı vaxtına çevirir"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(BAKU_TIMEZONE)

def baku_now_for_history():
    """History logger üçün ISO format Bakı vaxtı"""
    return get_baku_time().isoformat()