# analyze_khepars_daily.py
# تحلیل روزانه خپارس
# اجرا: python analyze_khepars_daily.py

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
    print(f"  📊 تحلیل خپارس")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    # جستجو
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
    close = float(found.get("Close") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    change = float(found.get("ChangePct") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    
    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

    print(f"  📌 خپارس")
    print()
    print(f"  💰 قیمت‌ها:")
    print(f"     Last:          {int(last):>8,}")
    print(f"     Close:         {int(close):>8,}")
    print(f"     Yesterday:     {int(yesterday):>8,}")
    print(f"     تغییر:         {change:>7.2f}%")
    print()
    print(f"  📊 دامنه:")
    print(f"     کف (MinAllowed):  {int(min_a):>8,}")
    print(f"     سقف (MaxAllowed): {int(max_a):>8,}")
    print()
    print(f"  📊 سفارشات:")
    print(f"     خرید حقیقی: {int(vol_buy):>15,}")
    print(f"     فروش حقیقی: {int(vol_sell):>15,}")
    print(f"     خرید حقوقی: {int(vol_buy_n):>15,}")
    print(f"     فروش حقوقی: {int(vol_sell_n):>15,}")
    print()

    # تشخیص
    if vol_buy > 0 and vol_sell == 0:
        print("  🟢 صف خرید!")
    elif vol_sell > 0 and vol_buy == 0:
        print("  🔴 صف فروش!")
    elif vol_buy > 0 and vol_sell > 0:
        ratio = vol_buy / vol_sell
        print(f"  📊 نسبت خرید/فروش: {ratio:.2f}")
    print()

    # محاسبات
    print("  📊 محاسبات -3%:")
    print(f"     از Yesterday ({int(yesterday):,}):")
    print(f"        خرید -3%:  {int(yesterday * 0.97):,}")
    print(f"        فروش +3%:  {int(yesterday * 1.03):,}")
    print()
    print(f"     از Last ({int(last):,}):")
    print(f"        خرید -3%:  {int(last * 0.97):,}")
    print(f"        فروش +3%:  {int(last * 1.03):,}")
    print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
