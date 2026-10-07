# refresh_ins_codes.py
# استخراج مجدد INS Codeها — هر روز صبح
# اجرا: python refresh_ins_codes.py

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
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

INS_CODES_FILE = PROJECT_ROOT / "data" / "all_ins_codes.json"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔄 استخراج مجدد INS Codeها")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # بارگذاری قبلی
    old_stocks = []
    if INS_CODES_FILE.exists():
        try:
            old_stocks = json.loads(INS_CODES_FILE.read_text(encoding="utf-8"))
            safe_print(f"  📊 قبلی: {len(old_stocks)} سهم")
        except:
            pass

    # دریافت جدید
    safe_print("  📡 دریافت داده جدید...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    # فیلتر
    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    # استخراج
    new_stocks = {}
    for _, row in df.iterrows():
        try:
            ins_code = str(row.get("InsCode") or "")
            symbol = str(row.get("Symbol", ""))
            name = str(row.get("Name", ""))

            if not ins_code or not symbol:
                continue

            # حذف حق تقدم
            if symbol.endswith("3") or symbol.endswith("ح"):
                continue

            new_stocks[ins_code] = {
                "ins_code": ins_code,
                "symbol": symbol,
                "name": name,
            }
        except:
            continue

    safe_print(f"  ✅ {len(new_stocks)} سهم جدید")
    safe_print("")

    # ترکیب
    combined = {}

    for s in old_stocks:
        combined[s["ins_code"]] = s

    for code, s in new_stocks.items():
        combined[code] = s

    # ذخیره
    stocks_list = list(combined.values())
    stocks_list.sort(key=lambda x: x["symbol"])

    with open(INS_CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks_list, f, ensure_ascii=False, indent=2)

    safe_print(f"  💾 ذخیره: {INS_CODES_FILE}")
    safe_print(f"  📊 کل: {len(stocks_list)} سهم")
    safe_print(f"     (قبلی: {len(old_stocks)}, جدید: {len(new_stocks)})")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
