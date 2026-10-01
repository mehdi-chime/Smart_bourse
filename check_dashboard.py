# check_dashboard.py
# چک داشبورد HTML
# اجرا: python check_dashboard.py

import os
import sys
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
HTML_FILE = PROJECT_ROOT / "reports" / "dashboard_v2.html"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 چک داشبورد")
    safe_print("=" * 80)
    safe_print("")

    if not HTML_FILE.exists():
        safe_print(f"  ❌ {HTML_FILE} پیدا نشد!")
        return

    # ۱. حجم
    size = HTML_FILE.stat().st_size
    safe_print(f"  📄 فایل: {HTML_FILE.name}")
    safe_print(f"  📏 حجم: {size:,} bytes")
    safe_print("")

    # ۲. محتوا
    content = HTML_FILE.read_text(encoding="utf-8")
    
    checks = [
        ("Smart_Bourse Dashboard", "عنوان"),
        ("آمار AI", "بخش آمار"),
        ("وزن‌های AI", "بخش وزن‌ها"),
        ("آخرین سیگنال‌ها", "بخش سیگنال‌ها"),
        ("money_flow", "وزن money_flow"),
        ("total_signals", "متغیر total_signals"),
    ]

    safe_print("  🔍 چک محتوا:")
    for text, desc in checks:
        if text in content:
            safe_print(f"     ✅ {desc}")
        else:
            safe_print(f"     ❌ {desc}")
    safe_print("")

    # ۳. باز کردن در مرورگر
    safe_print("  🌐 باز کردن در مرورگر...")
    import webbrowser
    webbrowser.open(f"file:///{HTML_FILE.as_posix()}")
    safe_print("     ✅ باز شد")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
