"""
config.py
تنظیمات مرکزی پروژه Smart Bourse
"""

# ========== تنظیمات عمومی پروژه ==========
PROJECT_NAME = "Smart Bourse"
VERSION = "0.1"
AUTHOR = "Mehdi Jalali"
DEBUG = True

# ========== تنظیمات بازار و معاملات ==========
MARKET_CONFIG = {
    "min_volume": 50_000_000_000,      # حداقل حجم معاملات (۵۰ میلیارد تومان)
    "trade_fee": 0.0125,               # کارمزد معاملات ۱.۲۵٪
    "min_profit": 0.02,                # حداقل سود قابل انتظار (۲٪)
    "max_candidates": 3,               # تعداد سهام برتر برای خروجی
}

# ========== تنظیمات سلامت بازار ==========
HEALTH_THRESHOLDS = {
    "RED": 35,
    "YELLOW": 65,
}

# ========== تنظیمات ایتا (Eitaa) ==========
EITAA_TOKEN = "bot502704:051f1884-444f-4db5-9332-510e4a2baa81"  # توکن ربات خود را اینجا بگذارید
EITAA_CHAT_ID = "367106316"  # شناسه کاربری خود را اینجا بگذارید
SEND_TO_EITAA = True  # برای فعال‌سازی، True کنید

# ========== تنظیمات پیش‌بینی ریزش ==========
DROP_PREDICTION = {
    "min_cash_required": 17_000_000,
    "alert_threshold": 0.6,
}
