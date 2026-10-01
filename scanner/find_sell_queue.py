# find_sell_queue.py
# پیدا کردن سهم‌های با صف فروش + امکان سود تا صفر تابلو
# اجرا: python find_sell_queue.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

MIN_VOLUME = 500_000
MIN_QUEUE_VALUE = 1_000_000_000  # 1 میلیارد


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
    print(f"  🔍 اسکن سهم‌های با صف فروش")
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
    # پیدا کردن صف فروش
    # ═══════════════════════════════════════════════════════
    sell_queue = []

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

            # صف فروش: Buy_retail = 0, Sell_retail > 0
            if vol_sell > MIN_VOLUME and vol_buy == 0:
                # فاصله تا صفر تابلو (قیمت دیروز)
                distance_to_zero = ((yesterday - last) / last) * 100
                
                # ارزش صف
                queue_value = vol_sell * last

                if queue_value >= MIN_QUEUE_VALUE:
                    sell_queue.append({
                        "symbol": symbol,
                        "price": last,
                        "yesterday": yesterday,
                        "change": change,
                        "vol_sell": vol_sell,
                        "queue_value": queue_value,
                        "distance_to_zero": distance_to_zero,
                    })
        except Exception:
            continue

    # مرتب‌سازی بر اساس ارزش صف
    sell_queue.sort(key=lambda x: -x["queue_value"])

    print("=" * 100)
    print(f"  🔴 سهم‌های با صف فروش")
    print("=" * 100)
    print()

    if sell_queue:
        print(f"  {'نماد':<12} | {'قیمت':>10} | {'تغییر':>8} | {'فاصله صفر':>10} | {'ارزش صف':>15}")
        print("  " + "-" * 85)

        for q in sell_queue[:30]:
            distance = q["distance_to_zero"]
            marker = ""

            if distance >= 3:
                marker = "⭐"  # سود ≥3%
            elif distance >= 2:
                marker = "✅"  # سود ≥2%
            elif distance >= 1:
                marker = "🟡"

            print(
                f"  {q['symbol'][:12]:<12} | "
                f"{int(q['price']):>10,} | "
                f"{q['change']:>7.2f}% | "
                f"{distance:>9.2f}% | "
                f"{int(q['queue_value']):>15,} {marker}"
            )

        print()
        print(f"  📊 تعداد: {len(sell_queue)}")
    else:
        print("  ❌ صف فروشی پیدا نشد")

    print()

    # ═══════════════════════════════════════════════════════
    # بهترین فرصت‌ها (فاصله > 2% تا صفر)
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print(f"  🎯 بهترین فرصت‌ها (سود ≥2% تا صفر تابلو)")
    print("=" * 100)
    print()

    best = [q for q in sell_queue if q["distance_to_zero"] >= 2.0]

    if best:
        print(f"  {'نماد':<12} | {'قیمت':>10} | {'فاصله صفر':>10} | {'ارزش صف':>15} | {'سود انتظاری':>12}")
        print("  " + "-" * 85)

        for q in best[:20]:
            profit = q["distance_to_zero"] - 1.25  # منهای کارمزد
            print(
                f"  {q['symbol'][:12]:<12} | "
                f"{int(q['price']):>10,} | "
                f"{q['distance_to_zero']:>9.2f}% | "
                f"{int(q['queue_value']):>15,} | "
                f"{profit:>11.2f}%"
            )

        print()
        print(f"  ✅ {len(best)} فرصت")
    else:
        print("  ❌ فرصتی با سود ≥2% نیست")

    print()
    print("=" * 100)
    print("  💡 استراتژی:")
    print("     1. سهم با صف فروش پیدا کن")
    print("     2. سفارش خرید بذار روی قیمت فعلی")
    print("     3. وقتی صف شکست → خودکار می‌خری")
    print("     4. صبر کن تا قیمت به صفر تابلو برسه")
    print("     5. بفروش → سود!")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
