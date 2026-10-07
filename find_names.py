# find_names.py
# پیدا کردن اسم دقیق سهم‌ها
# اجرا: python find_names.py

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
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 پیدا کردن اسم دقیق")
    safe_print("=" * 80)
    safe_print("")

    df = att.get_live_market()
    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    # جستجو
    search_terms = ["شپنا", "شتران", "پالایش", "نفت"]

    for term in search_terms:
        safe_print(f"  🔍 {term}:")
        count = 0
        for _, row in df.iterrows():
            symbol = str(row.get("Symbol", ""))
            name = str(row.get("Name", ""))

            if term in symbol or term in name:
                safe_print(f"     ✅ {symbol} | {name} | {row.get('InsCode')}")
                count += 1
                if count >= 10:
                    break
        safe_print("")

    safe_print("=" * 80)


if __name__ == "__main__":
    main()
