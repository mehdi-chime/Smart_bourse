# check_dafra_now.py
# چک دقیق دفرا
# اجرا: python check_dafra_now.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

SYMBOL = "دفرا"


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
    print(f"  🔍 چک دقیق {SYMBOL}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    found = None
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if normalize(symbol) == normalize(SYMBOL):
            found = row
            break

    if found is None:
        print(f"  ❌ {SYMBOL} پیدا نشد")
        return

    print(f"  📌 {SYMBOL}")
    print(f"     Name: {found.get('Name', '?')}")
    print()

    # قیمت‌ها
    print("  💰 قیمت‌ها:")
    for col in ["Last", "Close", "Yesterday", "PreviousClose",
                "Open", "FirstPrice", "High", "Low",
                "MinAllowed", "MaxAllowed", "ChangePct"]:
        try:
            val = found.get(col)
            print(f"     {col:15}: {val}")
        except:
            pass
    print()

    # سفارشات
    print("  📊 سفارشات:")
    for col in ["Vol_buy_retail", "Vol_sell_retail",
                "Vol_buy_institutional", "Vol_sell_institutional",
                "Buy_I_Count", "Sell_I_Count",
                "Buy_N_Count", "Sell_N_Count"]:
        try:
            val = found.get(col)
            print(f"     {col:25}: {val}")
        except:
            pass
    print()

    # Order Book
    print("  📋 Order Book (5 سطح):")
    print()
    for i in range(1, 6):
        bid_p = found.get(f"BidPrice{i}")
        bid_v = found.get(f"BidVolume{i}")
        ask_p = found.get(f"AskPrice{i}")
        ask_v = found.get(f"AskVolume{i}")
        print(f"     سطح {i}:")
        print(f"        🟢 خرید: {bid_p} ({bid_v})")
        print(f"        🔴 فروش: {ask_p} ({ask_v})")
    print()

    # محاسبات
    last = float(found.get("Last") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

    if last > 0:
        print("  📊 محاسبات:")
        print(f"     Last:       {int(last):,}")
        print(f"     Yesterday:  {int(yesterday):,}")
        print(f"     کف:         {int(min_a):,}")
        print(f"     سقف:        {int(max_a):,}")
        print()

        # فاصله
        if min_a > 0:
            distance = (last - min_a) / min_a * 100
            print(f"     فاصله از کف:  {distance:.2f}%")
        if max_a > 0:
            distance = (max_a - last) / last * 100
            print(f"     فاصله از سقف: {distance:.2f}%")
        print()

    # تحلیل
    print("  🎯 تحلیل:")
    print()
    
    if last == max_a:
        print("     🟢 صف خرید! (Last = سقف)")
    elif last == min_a:
        print("     🔴 صف فروش! (Last = کف)")
    else:
        print(f"     🟡 متعادل")
    print()

    if vol_buy_n > vol_sell_n:
        print(f"     🟢 حقوقی خریدار")
        print(f"        خرید: {int(vol_buy_n):,}")
        print(f"        فروش: {int(vol_sell_n):,}")
    elif vol_sell_n > vol_buy_n:
        print(f"     🔴 حقوقی فروشنده")
    else:
        print(f"     🟡 حقوقی متعادل")
    print()

    # استراتژی
    print("  🎯 استراتژی:")
    print(f"     🟢 سفارش خرید:  {int(min_a):,}")
    print(f"     🔴 سفارش فروش:  {int(max_a):,}")
    print(f"     ⛔ حد ضرر:       {int(min_a * 0.98):,}")
    print()

    print("=" * 90)
    print()


if __name__ == "__main__":
    main()
