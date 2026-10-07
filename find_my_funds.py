# find_my_funds.py
# پیدا کردن INS Code صندوق‌های من
# اجرا: python find_my_funds.py

import os
import sys
import json
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
FUNDS_FILE = PROJECT_ROOT / "data" / "real_funds.json"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 پیدا کردن صندوق‌های من")
    safe_print("=" * 80)
    safe_print("")

    if not FUNDS_FILE.exists():
        safe_print(f"  ❌ {FUNDS_FILE} پیدا نشد!")
        return

    funds = json.loads(FUNDS_FILE.read_text(encoding="utf-8"))
    safe_print(f"  📊 {len(funds)} صندوق در لیست")
    safe_print("")

    # جستجو
    search_terms = [
        "طلا", "زر", "نقره", "اهرمی", "اهرم",
        "درآمد ثابت", "درآمدثابت", "سهامی", "سهام",
        "شاخصی", "کالا", "بخشی", "مختلط", "املاک",
    ]

    for term in search_terms:
        safe_print(f"  🔍 جستجو: {term}")
        count = 0

        for f in funds:
            if term in f.get("name", ""):
                safe_print(f"     ✅ {f['symbol']:15} | {f['name'][:60]:60} | {f['ins_code']}")
                count += 1
                if count >= 10:
                    break

        if count == 0:
            safe_print(f"     ❌ پیدا نشد")
        safe_print("")

    safe_print("=" * 80)


if __name__ == "__main__":
    main()
