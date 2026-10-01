# fix_hunter_target.py
# اصلاح هدف‌های hunter با MinAllowed/MaxAllowed
# اجرا: python fix_hunter_target.py

import sys
import json
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
    print("=" * 110)
    print(f"  🔧 اصلاح هدف‌های hunter با MinAllowed/MaxAllowed")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)
    print()

    # ۱. دریافت داده زنده
    print("  📡 دریافت داده از TSETMC...")
    df = att.get_live_market()

    if df is None or df.empty:
        print("  ❌ خطا در دریافت داده")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  ✅ {len(df)} سهم")
    print()

    # ۲. خواندن آخرین hunter
    hunter_dir = PROJECT_ROOT / "data" / "hunter"
    hunter_files = sorted(hunter_dir.glob("hunter_*.json"))
    if not hunter_files:
        print("  ❌ فایل hunter پیدا نشد")
        print("     اول اجرا کن: python scanner\\opportunity_hunter_v54.py")
        return

    latest = hunter_files[-1]
    print(f"  📁 آخرین hunter: {latest.name}")

    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    print(f"  📊 {len(results)} سهم از hunter")
    print()

    # ۳. اصلاح هدف‌ها
    print("=" * 110)
    print(f"  🎯 مقایسه هدف‌ها (hunter vs بورس)")
    print("=" * 110)
    print()

    print(f"  {'#':<3} | {'نماد':<10} | {'Last':>8} | {'Yesterday':>9} | {'کف بورس':>9} | {'سقف بورس':>9} | {'hunter خرید':>11} | {'بورس خرید':>10} | {'اختلاف':>7}")
    print("  " + "-" * 107)

    fixed = []

    for i, r in enumerate(results, 1):
        symbol = r["symbol"]

        # پیدا کردن در df
        found = None
        for _, row in df.iterrows():
            live_symbol = str(row.get("Symbol", ""))
            if normalize(live_symbol) == normalize(symbol):
                found = row
                break

        if found is None:
            continue

        last = float(found.get("Last") or found.get("Close") or 0)
        yesterday = float(found.get("Yesterday") or 0)
        min_a = float(found.get("MinAllowed") or 0)
        max_a = float(found.get("MaxAllowed") or 0)

        hunter_buy = r["buy_target"]
        hunter_sell = r["sell_target"]
        hunter_stop = r.get("stop_loss", 0)
        rsi = r.get("rsi", 0)

        if min_a > 0 and max_a > 0:
            diff = hunter_buy - min_a

            # حد ضرر جدید: -2% از خرید بورس
            new_stop = round(min_a * 0.98)

            fixed.append({
                "symbol": symbol,
                "last": last,
                "yesterday": yesterday,
                "min_allowed": min_a,
                "max_allowed": max_a,
                "hunter_buy": hunter_buy,
                "hunter_sell": hunter_sell,
                "hunter_stop": hunter_stop,
                "rsi": rsi,
                "buy_target": min_a,
                "sell_target": max_a,
                "stop_loss": new_stop,
                "diff": diff,
            })

            print(
                f"  {i:<3} | "
                f"{symbol[:10]:<10} | "
                f"{int(last):>8,} | "
                f"{int(yesterday):>9,} | "
                f"{int(min_a):>9,} | "
                f"{int(max_a):>9,} | "
                f"{int(hunter_buy):>11,} | "
                f"{int(min_a):>10,} | "
                f"{int(diff):>+7,}"
            )

    print()
    print(f"  ✅ {len(fixed)} سهم اصلاح شد")
    print()

    # ۴. ذخیره
    output = PROJECT_ROOT / "data" / "hunter" / f"fixed_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": latest.name,
            "count": len(fixed),
            "fixed": fixed,
        }, f, ensure_ascii=False, indent=2)

    print(f"  💾 ذخیره: {output}")
    print()

    # ۵. بهترین ۱۰ سهم (بر اساس RSI پایین)
    print("=" * 110)
    print(f"  🏆 بهترین ۱۰ سهم (هدف دقیق بورس)")
    print("=" * 110)
    print()

    fixed.sort(key=lambda x: x.get("rsi", 100))

    print(f"  {'#':<3} | {'نماد':<10} | {'Last':>8} | {'RSI':>5} | {'🟢 خرید':>9} | {'🔴 فروش':>9} | {'⛔ حدضرر':>9} | {'سود':>6}")
    print("  " + "-" * 90)

    for i, r in enumerate(fixed[:10], 1):
        # سود خالص
        profit = (r["sell_target"] / r["buy_target"] - 1) * 100 - 1.25
        print(
            f"  {i:<3} | "
            f"{r['symbol'][:10]:<10} | "
            f"{int(r['last']):>8,} | "
            f"{r['rsi']:>5} | "
            f"{int(r['buy_target']):>9,} | "
            f"{int(r['sell_target']):>9,} | "
            f"{int(r['stop_loss']):>9,} | "
            f"{profit:>5.2f}%"
        )

    print()

    # ۶. آمار
    print("=" * 110)
    print(f"  📊 آمار")
    print("=" * 110)
    print()

    if fixed:
        diffs = [abs(f["diff"]) for f in fixed]
        print(f"  میانگین اختلاف hunter با بورس: {sum(diffs)/len(diffs):.1f} ریال")
        print(f"  بیشترین اختلاف: {max(diffs):.0f} ریال")
        print(f"  کمترین اختلاف: {min(diffs):.0f} ریال")
        print()

    print("=" * 110)
    print(f"  ✅ تمام شد!")
    print("=" * 110)
    print()


if __name__ == "__main__":
    main()
