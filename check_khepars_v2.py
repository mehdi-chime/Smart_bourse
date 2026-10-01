# check_khepars_v2.py
# چک دقیق خپارس با InsCode
# اجرا: python check_khepars_v2.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

INSCODE = "25211433301660888"


def main():
    print()
    print("=" * 80)
    print(f"  🔍 چک خپارس با InsCode")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    print(f"  ✅ {len(df)} ردیف")
    print()
    print(f"  📋 ستون‌ها:")
    for i, c in enumerate(df.columns):
        print(f"     {i}. {c}")
    print()

    # جستجو با InsCode
    print(f"  🔍 جستجوی InsCode: {INSCODE}")
    print()

    # چک ستون InsCode
    if "InsCode" in df.columns:
        found = df[df["InsCode"] == INSCODE]
        if not found.empty:
            row = found.iloc[0]
            print(f"  ✅ پیدا شد با InsCode!")
            print()
            for col in df.columns:
                try:
                    print(f"     {col}: {row[col]}")
                except:
                    pass
            return
        else:
            print(f"  ❌ با InsCode پیدا نشد")

    # جستجو با اسم
    print()
    print(f"  🔍 جستجوی اسم:")
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        name = str(row.get("Name", ""))
        if "خپارس" in symbol or "خپارس" in name or "پارس" in symbol:
            print(f"     ✅ {symbol} - {name}")
            print()
            for col in df.columns:
                try:
                    print(f"        {col}: {row[col]}")
                except:
                    pass
            print()

    # جستجو با InsCode تو همه ستون‌ها
    print()
    print(f"  🔍 جستجوی InsCode تو همه ستون‌ها:")
    for col in df.columns:
        try:
            if INSCODE in df[col].astype(str).values:
                found = df[df[col].astype(str) == INSCODE]
                if not found.empty:
                    print(f"     ✅ پیدا شد در ستون {col}")
                    row = found.iloc[0]
                    print(f"        Symbol: {row.get('Symbol', '?')}")
                    print(f"        Name: {row.get('Name', '?')}")
                    return
        except:
            continue


if __name__ == "__main__":
    main()
