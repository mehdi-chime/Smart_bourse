# upgrade_v10.py
# ارتقای v10 با alert_manager + update_portfolio
# اجرا: python upgrade_v10.py

import os
import sys
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 ارتقای v10")
    safe_print("=" * 80)
    safe_print("")

    # لیست کارهای باقی‌مونده
    tasks = [
        {
            "name": "alert_manager به v10",
            "desc": "اضافه کردن هشدار خودکار به school_mode_v10",
            "priority": "🔴 فوری",
        },
        {
            "name": "update_portfolio به v10",
            "desc": "اضافه کردن رصد پرتفوی به v10",
            "priority": "🔴 فوری",
        },
        {
            "name": "فیلتر RSI 22-28 به اسکنر",
            "desc": "اضافه کردن فیلتر طلایی به smart_scanner_v8",
            "priority": "🔴 فوری",
        },
        {
            "name": "نصب مجدد Refresh Task",
            "desc": "برای سهم‌های جدید",
            "priority": "🟡 مهم",
        },
        {
            "name": "تحلیل پکویر",
            "desc": "از نقشه‌راه ۴",
            "priority": "🟡 مهم",
        },
        {
            "name": "بهینه‌سازی AI",
            "desc": "improve_ai_v5.py",
            "priority": "🟢 خوب",
        },
    ]

    safe_print("  📋 کارهای باقی‌مونده:")
    safe_print("")

    for i, t in enumerate(tasks, 1):
        safe_print(f"  {i}. {t['priority']} {t['name']}")
        safe_print(f"     {t['desc']}")
        safe_print("")

    safe_print("=" * 80)
    safe_print("  📌 پیشنهاد:")
    safe_print("")
    safe_print("  اول: alert_manager + update_portfolio به v10")
    safe_print("  دوم: فیلتر RSI 22-28 به اسکنر")
    safe_print("  سوم: نصب مجدد Refresh")
    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
