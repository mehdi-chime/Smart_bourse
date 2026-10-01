# analyze_dalbar_deep.py
# تحلیل عمیق دالبر
# اجرا: python analyze_dalbar_deep.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

SYMBOL = "دالبر"


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
    print(f"  📊 تحلیل عمیق {SYMBOL}")
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

    last = float(found.get("Last") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    change = float(found.get("ChangePct") or 0)
    
    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)
    
    ask_1 = float(found.get("AskPrice1") or 0)
    ask_v1 = float(found.get("AskVolume1") or 0)
    bid_1 = float(found.get("BidPrice1") or 0)
    bid_v1 = float(found.get("BidVolume1") or 0)

    print(f"  📌 {SYMBOL} - {found.get('Name', '?')}")
    print()
    print(f"  💰 قیمت‌ها:")
    print(f"     Last:        {int(last):>10,}")
    print(f"     Yesterday:   {int(yesterday):>10,}")
    print(f"     کف:          {int(min_a):>10,}")
    print(f"     سقف:         {int(max_a):>10,}")
    print(f"     تغییر:       {change:>9.2f}%")
    print()

    # صف فروش
    print(f"  🔴 صف فروش:")
    print(f"     Ask1:        {int(ask_1):>10,} ({int(ask_v1):>15,})")
    print(f"     Bid1:        {int(bid_1):>10,} ({int(bid_v1):>15,})")
    print()
    
    if ask_v1 > 0 and bid_v1 > 0:
        ratio = ask_v1 / bid_v1
        print(f"     نسبت صف فروش: {ratio:.0f}x")
    print()

    # حقوقی/حقیقی
    print(f"  📊 حقوقی/حقیقی:")
    print(f"     حقوقی خرید: {int(vol_buy_n):>15,}")
    print(f"     حقوقی فروش: {int(vol_sell_n):>15,}")
    if vol_buy_n > vol_sell_n:
        print(f"     🟢 حقوقی خریدار ({vol_buy_n/vol_sell_n:.1f}x)")
    else:
        print(f"     🔴 حقوقی فروشنده")
    print()
    print(f"     حقیقی خرید: {int(vol_buy):>15,}")
    print(f"     حقیقی فروش: {int(vol_sell):>15,}")
    if vol_buy > vol_sell:
        print(f"     🟢 حقیقی خریدار")
    else:
        print(f"     🔴 حقیقی فروشنده")
    print()

    # استراتژی
    print("  🎯 استراتژی:")
    print(f"     🟢 خرید:     {int(min_a):>10,} (کف)")
    print(f"     🔴 فروش:     {int(max_a):>10,} (سقف)")
    print(f"     ⛔ حد ضرر:    {int(min_a * 0.98):>10,}")
    profit = (max_a / min_a - 1) * 100 - 1.25
    print(f"     💰 سود:     {profit:>9.2f}%")
    print()

    # مقایسه با خپارس
    print("  📊 مقایسه با خپارس (دیروز):")
    print(f"     خپارس: صف فروش 200M → +5.29%")
    print(f"     دالبر: صف فروش {int(ask_v1/1_000_000)}M → ?")
    print()

    # تصمیم
    print("=" * 90)
    print("  🎯 تصمیم:")
    print("=" * 90)
    print()
    
    if vol_buy_n > vol_sell_n and ask_v1 > 1_000_000:
        print("  ✅ شبیه خپارس!")
        print("  ✅ حقوقی خریدار")
        print("  ✅ صف فروش")
        print("  ✅ فرصت خرید!")
        print()
        print(f"  💡 سفارش خرید: {int(min_a):,}")
        print(f"  💡 سفارش فروش: {int(max_a):,}")
        print(f"  💡 حد ضرر: {int(min_a * 0.98):,}")
    else:
        print("  🟡 با احتیاط")
    
    print()
    print("=" * 90)
    print()


if __name__ == "__main__":
    main()
