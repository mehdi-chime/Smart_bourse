# check_orders.py
# چک سفارشات -3%
# اجرا: python check_orders.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

# سفارشات تو
MY_ORDERS = {
    "خبهمن": {"target": 2387, "percent": -3.0},
    "ستران":  {"target": 13211, "percent": -3.0},
    "دفرا":   {"target": 45609, "percent": -3.0},
}


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
    print("=" * 90)
    print(f"  📊 چک سفارشات -3%")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  ✅ {len(df)} سهم")
    print()

    for symbol, order in MY_ORDERS.items():
        found = None
        for _, row in df.iterrows():
            live_symbol = str(row.get("Symbol", ""))
            if normalize(live_symbol) == normalize(symbol):
                found = row
                break

        if found is None:
            print(f"  ❌ {symbol}: پیدا نشد")
            continue

        current = float(found.get("Last") or found.get("Close") or 0)
        change = float(found.get("ChangePct") or 0)
        yesterday = float(found.get("Yesterday") or 0)

        target = order["target"]
        target_pct = order["percent"]

        # فاصله تا هدف
        if yesterday > 0:
            target_from_yesterday = (target - yesterday) / yesterday * 100
        else:
            target_from_yesterday = 0

        print(f"  📌 {symbol}")
        print(f"     💰 قیمت فعلی:  {int(current):,}")
        print(f"     📊 تغییر:      {change:+.2f}%")
        print(f"     🎯 خرید هدف:   {int(target):,} ({target_pct}%)")
        print(f"     📊 قیمت دیروز: {int(yesterday):,}")
        print()

        # چک
        if current <= target:
            print(f"     ✅ الآن ≤ خرید هدف! می‌تونی بخری!")
        else:
            diff = (current - target) / target * 100
            print(f"     ⏳ {diff:.1f}% بالاتر از خرید هدف")
            print(f"     💡 صبر کن...")

        print()
        print("  " + "-" * 80)
        print()


if __name__ == "__main__":
    main()
