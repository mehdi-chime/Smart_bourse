# get_all_ins_codes.py
# استخراج INS Code همه سهم‌ها
# اجرا: python get_all_ins_codes.py

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


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 استخراج INS Code همه سهم‌ها")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # دریافت
    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    # فیلتر سهام عادی
    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]
        safe_print(f"     ✅ {len(df)} سهم عادی")
        safe_print("")

    # استخراج
    stocks = []

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

            stocks.append({
                "ins_code": ins_code,
                "symbol": symbol,
                "name": name,
            })
        except:
            continue

    safe_print(f"  ✅ {len(stocks)} سهم معتبر")
    safe_print("")

    # ذخیره
    output = PROJECT_ROOT / "data" / "all_ins_codes.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

    safe_print(f"  💾 ذخیره: {output}")
    safe_print(f"     ({len(stocks)} سهم)")
    safe_print("")

    # نمونه
    safe_print("  📋 نمونه (۲۰ تا اول):")
    for s in stocks[:20]:
        safe_print(f"     {s['ins_code']} | {s['symbol']} | {s['name'][:40]}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
