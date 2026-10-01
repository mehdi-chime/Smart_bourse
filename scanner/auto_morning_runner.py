# check_kefra_v2.py
# چک دقیق کفرا
# اجرا: python check_kefra_v2.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

SYMBOL = "كفرا"


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
    print(f"  📊 چک دقیق {SYMBOL}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    found = None
    for _, row in df.iterrows():
        live_symbol = str(row.get("Symbol", ""))
        if normalize(live_symbol) == normalize(SYMBOL):
            found = row
            break

    if found is None:
        print(f"  ❌ {SYMBOL} پیدا نشد")
        return

    # همه قیمت‌های ممکن
    last = float(found.get("Last") or found.get("Close") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    prev_close = float(found.get("PreviousClose") or 0)
    low = float(found.get("Low") or 0)
    high = float(found.get("High") or 0)
    open_p = float(found.get("Open") or 0)
    first_p = float(found.get("FirstPrice") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    change = float(found.get("ChangePct") or 0)

    print(f"  📌 {SYMBOL}")
    print()
    print(f"  💰 قیمت‌های مختلف:")
    print(f"     Last:            {int(last):,}")
    print(f"     Close:           {int(found.get('Close') or 0):,}")
    print(f"     Yesterday:       {int(yesterday):,}")
    print(f"     PreviousClose:   {int(prev_close):,}")
    print(f"     Open:            {int(open_p):,}")
    print(f"     FirstPrice:      {int(first_p):,}")
    print(f"     High:            {int(high):,}")
    print(f"     Low:             {int(low):,}")
    print(f"     MaxAllowed:      {int(max_a):,}")
    print(f"     MinAllowed:      {int(min_a):,}")
    print()
    print(f"  📊 تغییر: {change:+.2f}%")
    print()

    # محاسبات
    print("  📊 محاسبات -3%:")
    print()
    
    for name, price in [
        ("Last", last),
        ("Yesterday", yesterday),
        ("PreviousClose", prev_close),
        ("Open", open_p),
        ("FirstPrice", first_p),
    ]:
        if price > 0:
            buy = round(price * 0.97)
            sell = round(price * 1.03)
            print(f"     از {name:15} ({int(price):>8,}):")
            print(f"        خرید -3%: {int(buy):>8,}")
            print(f"        فروش +3%: {int(sell):>8,}")
            print()

    # محاسبه منهای 3%
    print(f"  🎯 هدف -3%:")
    if last > 0:
        target = last * 0.97
        print(f"     Last × 0.97 = {target:.2f} → {round(target):,}")
    
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
