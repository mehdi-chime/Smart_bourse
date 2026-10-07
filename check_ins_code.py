# check_ins_code.py
# چک INS Code در algotik_tse
# اجرا: python check_ins_code.py

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
    safe_print("  🔍 چک INS Code")
    safe_print("=" * 80)
    safe_print("")

    df = att.get_live_market()
    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    # ستون‌ها
    safe_print("  📋 ستون‌ها:")
    for col in df.columns:
        safe_print(f"     - {col}")
    safe_print("")

    # INS Code
    safe_print("  🔍 جستجوی INS Code 211433301660888:")

    for _, row in df.iterrows():
        for col in df.columns:
            val = str(row.get(col, ""))
            if "211433301660888" in val:
                safe_print(f"     ✅ پیدا شد در {col}:")
                safe_print(f"        Symbol: {row.get('Symbol')}")
                safe_print(f"        Name: {row.get('Name')}")
                safe_print(f"        Value: {val}")
                safe_print("")

    # لیست سهم‌های پارس
    safe_print("  📋 سهم‌های با 'پارس':")
    count = 0
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        name = str(row.get("Name", ""))
        if "پارس" in symbol or "پارس" in name or "خپ" in symbol:
            safe_print(f"     - {symbol} ({name})")
            count += 1
            if count >= 15:
                break
    safe_print("")


if __name__ == "__main__":
    main()
