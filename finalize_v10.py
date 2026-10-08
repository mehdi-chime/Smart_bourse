# finalize_v10.py
# نهایی کردن v10 — RSI 22-28
# اجرا: python finalize_v10.py

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
V10_FILE = PROJECT_ROOT / "school_mode_v10.py"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🏆 نهایی کردن v10")
    safe_print("=" * 80)
    safe_print("")

    if not V10_FILE.exists():
        safe_print(f"  ❌ {V10_FILE} پیدا نشد!")
        return

    content = V10_FILE.read_text(encoding="utf-8")

    # چک تکراری
    if "RSI 22-28" in content or "RSI_GOLDEN" in content:
        safe_print("  ℹ️ از قبل نهایی شده!")
        return

    # اضافه کردن به تابع get_dynamic_rsi_range
    old_func = '''def get_dynamic_rsi_range(market):
    """تعیین بازه RSI داینامیک"""
    if not market:
        return 22, 28, "معمولی"

    market_pct = market["market_pct"]

    # بازار خیلی داغ
    if market_pct > 70:
        return 28, 38, "خیلی داغ"
    # بازار داغ
    elif market_pct > 55:
        return 28, 40, "داغ"
    # بازار معمولی
    elif market_pct > 45:
        return 25, 35, "معمولی"
    # بازار سرد
    elif market_pct > 30:
        return 22, 30, "سرد"
    # بازار خیلی سرد
    else:
        return 18, 28, "خیلی سرد"'''

    new_func = '''def get_dynamic_rsi_range(market):
    """تعیین بازه RSI — فیلتر طلایی (88.1% Win Rate)"""
    # همیشه RSI 22-28 — بهترین بازه
    return 22, 28, "طلایی"'''

    if old_func in content:
        content = content.replace(old_func, new_func, 1)
        safe_print("  ✅ تابع داینامیک → طلایی")
    else:
        safe_print("  ⚠️ الگو پیدا نشد")

    # ذخیره
    V10_FILE.write_text(content, encoding="utf-8")
    safe_print("")
    safe_print(f"  💾 ذخیره: {V10_FILE}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
