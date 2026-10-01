# check_dcapsul_v2.py
# چک دکپسول با InsCode
# اجرا: python check_dcapsul_v2.py

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
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

INSCODE = "52382684379473036"


def main():
    print()
    print("=" * 90)
    print(f"  Check دکپسول")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ERR")
        return

    print(f"  Kol: {len(df)}")
    print()

    # جستجو با InsCode
    found = None
    for _, row in df.iterrows():
        inscode = str(row.get("InsCode", ""))
        if inscode == INSCODE:
            found = row
            break

    if found is None:
        print(f"  {INSCODE} peyda nashod")
        print()
        # جستجو با کلمه
        print("  Jostojoo ba 'کپسول':")
        for _, row in df.iterrows():
            symbol = str(row.get("Symbol", ""))
            name = str(row.get("Name", ""))
            if "کپسول" in symbol or "کپسول" in name or "زالین" in name or "دکپ" in symbol:
                print(f"     {symbol} - {name}")
        return

    print(f"  PEYDA SHOD!")
    print()
    for col in df.columns:
        try:
            print(f"     {col}: {found[col]}")
        except:
            pass

    print()
    print("=" * 90)
    print()


if __name__ == "__main__":
    main()
