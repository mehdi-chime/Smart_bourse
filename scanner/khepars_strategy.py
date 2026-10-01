# khepars_strategy.py
# استراتژی خپارس
# اجرا: python khepars_strategy.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


def normalize(s):
    if not s:
        return s
    return (str(s)
            .replace("\u0643", "\u06a9")
            .replace("\u064a", "\u06cc")
            .replace("\u0649", "\u06cc")
            .replace("\u0629", "\u0647")
            .replace("\u0640", "")
            .strip())


def main():
    print()
    print("=" * 80)
    print(f"  🎯 استراتژی خپارس")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    found = None
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if "خپارس" in symbol or "خپارس" in normalize(symbol):
            found = row
            break

    if found is None:
        print("  ❌ خپارس پیدا نشد")
        return

    last = float(found.get("Last") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    
    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

    print(f"  📌 خپارس")
    print()
    print(f"  💰 قیمت‌ها:")
    print(f"     Last:      {int(last):>8,}")
    print(f"     Yesterday: {int(yesterday):>8,}")
    print(f"     کف:        {int(min_a):>8,}")
    print(f"     سقف:       {int(max_a):>8,}")
    print()

    # تحلیل حقوقی/حقیقی
    if vol_buy_n > vol_sell_n:
        print(f"  🟢 حقوقی خریدار!")
        print(f"     خرید: {int(vol_buy_n):,}")
        print(f"     فروش: {int(vol_sell_n):,}")
        print(f"     نسبت: {vol_buy_n/vol_sell_n:.1f}x")
    else:
        print(f"  🔴 حقوقی فروشنده!")
    print()

    if vol_buy > vol_sell:
        print(f"  🟢 حقیقی خریدار!")
    else:
        print(f"  🔴 حقیقی فروشنده!")
    print()

    # استراتژی
    print("=" * 80)
    print("  🎯 استراتژی پیشنهادی")
    print("=" * 80)
    print()

    print(f"  🟢 سفارش خرید:  {int(min_a):,} (کف)")
    print(f"  🔴 سفارش فروش:  {int(max_a):,} (سقف)")
    print(f"  ⛔ حد ضرر:       {int(min_a * 0.98):,} (-2%)")
    print()
    print(f"  💰 سود ناخالص:  {((max_a / min_a) - 1) * 100:.2f}%")
    print(f"  💰 سود خالص:    {((max_a / min_a) - 1) * 100 - 1.25:.2f}%")
    print()

    print("=" * 80)
    print("  💡 تحلیل:")
    print("=" * 80)
    print()
    
    if vol_buy_n > vol_sell_n * 3:
        print("  ✅ حقوقی قوی خریدار")
        print("  ✅ احتمال برگشت بالا")
        print("  ✅ فرصت خرید!")
    else:
        print("  🟡 حقوقی خریدار ولی نه قوی")
    
    print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
