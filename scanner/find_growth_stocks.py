# find_growth_stocks.py
# پیدا کردن سهم‌های با پتانسیل رشد 0% تا +3%
# اجرا: python find_growth_stocks.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(__file__).parent.resolve()
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
    print("=" * 100)
    print(f"  🚀 اسکن سهم‌های با پتانسیل رشد 0% تا +3%")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  ✅ {len(df)} سهم")
    print()

    # ═══════════════════════════════════════════════════════
    # پیدا کردن سهم‌های با پتانسیل
    # ═══════════════════════════════════════════════════════
    candidates = []

    for _, row in df.iterrows():
        try:
            symbol = str(row.get("Symbol", ""))
            if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
                continue

            last = float(row.get("Last") or row.get("Close") or 0)
            yesterday = float(row.get("Yesterday") or 0)
            change = float(row.get("ChangePct") or 0)
            vol_buy = float(row.get("Vol_buy_retail") or 0)
            vol_sell = float(row.get("Vol_sell_retail") or 0)

            if last <= 0 or yesterday <= 0:
                continue

            # نسبت خرید/فروش
            if vol_sell > 0:
                ratio = vol_buy / vol_sell
            elif vol_buy > 0:
                ratio = 9999
            else:
                ratio = 0

            # ═══════════════════════════════════════════════════════
            # فیلترها برای رشد 0% تا +3%
            # ═══════════════════════════════════════════════════════
            # ۱. تغییر: بین -1% تا +1% (نزدیک صفر تابلو)
            if not (-1 <= change <= 1):
                continue

            # ۲. نسبت خرید/فروش: > 1.5 (خرید قوی)
            if ratio < 1.5:
                continue

            # ۳. حجم: > 500K
            total_vol = vol_buy + vol_sell
            if total_vol < 500_000:
                continue

            # فاصله تا سقف (+3%)
            distance_to_3pct = 3.0 - change

            # فاصله تا سقف مجاز (MaxAllowed)
            max_allowed = float(row.get("MaxAllowed") or 0)
            if max_allowed > 0:
                distance_to_max = ((max_allowed - last) / last) * 100
            else:
                distance_to_max = 3.0 - change

            candidates.append({
                "symbol": symbol,
                "price": last,
                "change": change,
                "ratio": ratio,
                "vol_buy": vol_buy,
                "vol_sell": vol_sell,
                "total_vol": total_vol,
                "distance_to_3pct": distance_to_3pct,
                "distance_to_max": distance_to_max,
                "max_allowed": max_allowed,
            })
        except Exception:
            continue

    # مرتب‌سازی بر اساس نسبت خرید
    candidates.sort(key=lambda x: -x["ratio"])

    print("=" * 100)
    print(f"  🚀 سهم‌های با پتانسیل رشد (تغییر -1% تا +1%، نسبت > 1.5)")
    print("=" * 100)
    print()

    if candidates:
        print(f"  {'#':<3} | {'نماد':<12} | {'قیمت':>10} | {'تغییر':>8} | {'نسبت':>8} | {'فاصله +3%':>10} | {'حجم':>15}")
        print("  " + "-" * 95)

        for i, c in enumerate(candidates[:30], 1):
            marker = ""
            if c["ratio"] >= 5:
                marker = "⭐⭐⭐"
            elif c["ratio"] >= 3:
                marker = "⭐⭐"
            elif c["ratio"] >= 2:
                marker = "⭐"

            print(
                f"  {i:<3} | "
                f"{c['symbol'][:12]:<12} | "
                f"{int(c['price']):>10,} | "
                f"{c['change']:>7.2f}% | "
                f"{c['ratio']:>8.2f} | "
                f"{c['distance_to_3pct']:>9.2f}% | "
                f"{int(c['total_vol']):>15,} {marker}"
            )

        print()
        print(f"  📊 تعداد: {len(candidates)}")
    else:
        print("  ❌ هیچ سهمی با این شرایط پیدا نشد")

    print()

    # ═══════════════════════════════════════════════════════
    # بهترین ۱۰ سهم
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print(f"  🏆 بهترین ۱۰ سهم برای رشد 0% تا +3%")
    print("=" * 100)
    print()

    if candidates:
        print(f"  {'#':<3} | {'نماد':<12} | {'قیمت':>10} | {'تغییر':>8} | {'نسبت':>8} | {'سود انتظاری':>12}")
        print("  " + "-" * 80)

        for i, c in enumerate(candidates[:10], 1):
            # سود انتظاری
            expected_profit = c["distance_to_3pct"] - 1.25  # منهای کارمزد
            print(
                f"  {i:<3} | "
                f"{c['symbol'][:12]:<12} | "
                f"{int(c['price']):>10,} | "
                f"{c['change']:>7.2f}% | "
                f"{c['ratio']:>8.2f} | "
                f"{expected_profit:>11.2f}%"
            )

    print()
    print("=" * 100)
    print("  💡 استراتژی:")
    print("     1. سهم با تغییر -1% تا +1% (نزدیک صفر)")
    print("     2. نسبت خرید/فروش > 1.5 (خرید قوی)")
    print("     3. سفارش خرید بذار روی قیمت فعلی")
    print("     4. صبر کن تا +3% بشه")
    print("     5. بفروش → سود!")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
