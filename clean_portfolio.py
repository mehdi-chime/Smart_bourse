# clean_portfolio.py
# پاک کردن سهم‌های فروخته‌شده
# اجرا: python clean_portfolio.py

import os
import sys
import json
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
PORTFOLIO_FILE = PROJECT_ROOT / "data" / "my_portfolio.json"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🧹 پاک کردن پرتفوی")
    safe_print("=" * 80)
    safe_print("")

    if not PORTFOLIO_FILE.exists():
        safe_print("  ❌ پرتفوی نیست!")
        return

    portfolio = json.loads(PORTFOLIO_FILE.read_text(encoding="utf-8"))

    safe_print(f"  📊 قبل: {len(portfolio)} سهم")
    safe_print("")

    # فیلتر: فقط سهم‌هایی که قیمت خرید و تعداد دارن
    cleaned = []
    removed = []

    for s in portfolio:
        buy_price = s.get("buy_price", 0)
        quantity = s.get("quantity", 0)

        if buy_price > 0 and quantity > 0:
            cleaned.append(s)
        else:
            removed.append(s["symbol"])

    # ذخیره
    PORTFOLIO_FILE.write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    safe_print(f"  ✅ بعد: {len(cleaned)} سهم")
    safe_print("")

    if removed:
        safe_print(f"  🗑️ حذف شده: {', '.join(removed)}")
        safe_print("")

    # نمایش
    safe_print("  📊 پرتفوی جدید:")
    safe_print("")
    for s in cleaned:
        safe_print(f"     {s['symbol']:15} | {s['buy_price']:>10,} | {s['quantity']:>10,}")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
