# detect_queue_trap.py
# تشخیص دام صف فروش
# اجرا: python detect_queue_trap.py

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
    print("=" * 100)
    print(f"  🎯 تشخیص دام صف فروش")
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

    traps = []
    real_sells = []

    for _, row in df.iterrows():
        try:
            symbol = str(row.get("Symbol", ""))
            if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
                continue

            last = float(row.get("Last") or row.get("Close") or 0)
            change = float(row.get("ChangePct") or 0)
            vol_buy = float(row.get("Vol_buy_retail") or 0)
            vol_sell = float(row.get("Vol_sell_retail") or 0)
            vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
            vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

            if last <= 0:
                continue

            # صف فروش: Sell_retail > 0, Buy_retail = 0
            if vol_sell > 0 and vol_buy == 0:
                # چک: حقوقی می‌خره؟
                if vol_buy_n > 0:
                    # حقوقی می‌خره → دام
                    traps.append({
                        "symbol": symbol,
                        "price": last,
                        "change": change,
                        "vol_sell": vol_sell,
                        "vol_buy_n": vol_buy_n,
                        "vol_sell_n": vol_sell_n,
                    })
                else:
                    # حقوقی نمی‌خره → واقعی
                    real_sells.append({
                        "symbol": symbol,
                        "price": last,
                        "change": change,
                        "vol_sell": vol_sell,
                        "vol_sell_n": vol_sell_n,
                    })
        except:
            continue

    # ═══════════════════════════════════════════════════════
    # دام صف فروش (حقوقی می‌خره!)
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print(f"  🟢 دام صف فروش (حقوقی می‌خره — فرصت خرید!)")
    print("=" * 100)
    print()

    if traps:
        traps.sort(key=lambda x: -x["vol_buy_n"])
        print(f"  {'نماد':<12} | {'قیمت':>10} | {'تغییر':>8} | {'صف فروش':>15} | {'خرید حقوقی':>15}")
        print("  " + "-" * 75)
        for t in traps[:20]:
            print(
                f"  {t['symbol'][:12]:<12} | "
                f"{int(t['price']):>10,} | "
                f"{t['change']:>7.2f}% | "
                f"{int(t['vol_sell']):>15,} | "
                f"{int(t['vol_buy_n']):>15,}"
            )
        print(f"\n  📊 تعداد: {len(traps)}")
    else:
        print("  ❌ دامی نیست")

    print()

    # ═══════════════════════════════════════════════════════
    # صف فروش واقعی
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print(f"  🔴 صف فروش واقعی (حقوقی می‌فروشه — خطر!)")
    print("=" * 100)
    print()

    if real_sells:
        real_sells.sort(key=lambda x: -x["vol_sell"])
        print(f"  {'نماد':<12} | {'قیمت':>10} | {'تغییر':>8} | {'صف فروش':>15} | {'فروش حقوقی':>15}")
        print("  " + "-" * 75)
        for r in real_sells[:20]:
            print(
                f"  {r['symbol'][:12]:<12} | "
                f"{int(r['price']):>10,} | "
                f"{r['change']:>7.2f}% | "
                f"{int(r['vol_sell']):>15,} | "
                f"{int(r['vol_sell_n']):>15,}"
            )
        print(f"\n  📊 تعداد: {len(real_sells)}")
    else:
        print("  ❌ صف فروش واقعی نیست")

    print()

    # ═══════════════════════════════════════════════════════
    # بررسی خپارس
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print(f"  🔍 بررسی خپارس")
    print("=" * 100)
    print()

    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if "خپارس" in symbol or "خپارس" in normalize(symbol):
            print(f"  📌 {symbol}")
            print()
            for col in ["Last", "ChangePct", "Vol_buy_retail", "Vol_sell_retail",
                        "Vol_buy_institutional", "Vol_sell_institutional",
                        "BidPrice1", "AskPrice1", "BidVolume1", "AskVolume1"]:
                try:
                    print(f"     {col}: {row[col]}")
                except:
                    pass
            print()

    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
