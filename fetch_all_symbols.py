# fetch_all_symbols.py
# ذخیره همه سهم‌ها
# اجرا: python fetch_all_symbols.py

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

OUTPUT = PROJECT_ROOT / "data" / "all_symbols.json"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  Fetch All Symbols")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  Daryaft dade...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ERR")
        return

    safe_print(f"  OK: {len(df)} rows")
    safe_print("")

    symbols = []
    for _, row in df.iterrows():
        try:
            symbol = str(row.get("Symbol", "")).strip()
            name = str(row.get("Name", "")).strip()
            inscode = str(row.get("InsCode", "")).strip()
            instrument = row.get("InstrumentType", 0)
            sector = str(row.get("SectorCode", "")).strip()
            eps = row.get("EPS", 0)
            shares = row.get("SharesOutstanding", 0)

            if not symbol:
                continue

            symbols.append({
                "symbol": symbol,
                "name": name,
                "inscode": inscode,
                "type": int(instrument) if instrument else 0,
                "sector": sector,
                "eps": float(eps) if eps else 0,
                "shares": float(shares) if shares else 0,
            })
        except:
            continue

    safe_print(f"  Total: {len(symbols)} symbols")
    safe_print("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "count": len(symbols),
            "symbols": symbols,
        }, f, ensure_ascii=False, indent=2)

    safe_print(f"  Save: {OUTPUT}")
    safe_print(f"  OK: {len(symbols)} sahm")
    safe_print("")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
