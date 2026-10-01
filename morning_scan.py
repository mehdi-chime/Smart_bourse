# morning_scan_v2.py
# اسکن صبحگاهی اصلاح‌شده
# اجرا: python morning_scan_v2.py

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
from datetime import datetime


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
    print(f"  🔍 اسکن صبحگاهی v2")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()

    print("  📡 دریافت داده از TSETMC...")
    df = att.get_live_market()

    if df is None or df.empty:
        print("  ❌ خطا")
        return

    print(f"  ✅ {len(df)} ردیف")

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  ✅ {len(df)} سهم")
    print()

    # ═══════════════════════════════════════════════════════
    # پیدا کردن وبیمه و بررسی دقیق
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print("  🔍 بررسی وبیمه (دقیق)")
    print("=" * 100)
    print()

    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if "وبيمه" in symbol or "وبیمه" in symbol or normalize(symbol) == normalize("وبیمه"):
            print(f"  📌 نماد: {symbol}")
            print()
            for col in df.columns:
                try:
                    val = row[col]
                    print(f"     {col}: {val}")
                except:
                    pass
            print()

    # ═══════════════════════════════════════════════════════
    # صف خرید/فروش قوی
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print("  🟢 صف خرید قوی (نسبت > 10)")
    print("=" * 100)
    print()

    queue_buy = []
    for _, row in df.iterrows():
        try:
            vol_buy = float(row.get("Vol_buy_retail") or 0)
            vol_sell = float(row.get("Vol_sell_retail") or 0)
            symbol = str(row.get("Symbol", ""))
            last = float(row.get("Last") or row.get("Close") or 0)
            change = float(row.get("ChangePct") or 0)

            if vol_buy > 0 and vol_sell == 0:
                queue_buy.append({
                    "symbol": symbol, "price": last,
                    "change": change, "vol_buy": vol_buy,
                    "type": "صف خرید"
                })
            elif vol_buy > 0 and vol_sell > 0:
                ratio = vol_buy / vol_sell
                if ratio > 10:
                    queue_buy.append({
                        "symbol": symbol, "price": last,
                        "change": change, "vol_buy": vol_buy,
                        "type": f"نسبت {ratio:.1f}"
                    })
        except:
            continue

    queue_buy.sort(key=lambda x: -x["vol_buy"])

    if queue_buy:
        print(f"  {'نماد':<12} | {'قیمت':>10} | {'تغییر':>8} | {'حجم خرید':>15} | {'نوع':>10}")
        print("  " + "-" * 75)
        for q in queue_buy[:20]:
            print(f"  {q['symbol'][:12]:<12} | {int(q['price']):>10,} | {q['change']:>7.2f}% | {int(q['vol_buy']):>15,} | {q['type']:>10}")
    else:
        print("  ❌ صف خرید قوی نیست")
    print()

    # ═══════════════════════════════════════════════════════
    # صف فروش قوی
    # ═══════════════════════════════════════════════════════
    print("=" * 100)
    print("  🔴 صف فروش قوی (نسبت > 10)")
    print("=" * 100)
    print()

    queue_sell = []
    for _, row in df.iterrows():
        try:
            vol_buy = float(row.get("Vol_buy_retail") or 0)
            vol_sell = float(row.get("Vol_sell_retail") or 0)
            symbol = str(row.get("Symbol", ""))
            last = float(row.get("Last") or row.get("Close") or 0)
            change = float(row.get("ChangePct") or 0)

            if vol_sell > 0 and vol_buy == 0:
                queue_sell.append({
                    "symbol": symbol, "price": last,
                    "change": change, "vol_sell": vol_sell,
                    "type": "صف فروش"
                })
            elif vol_sell > 0 and vol_buy > 0:
                ratio = vol_sell / vol_buy
                if ratio > 10:
                    queue_sell.append({
                        "symbol": symbol, "price": last,
                        "change": change, "vol_sell": vol_sell,
                        "type": f"نسبت {ratio:.1f}"
                    })
        except:
            continue

    queue_sell.sort(key=lambda x: -x["vol_sell"])

    if queue_sell:
        print(f"  {'نماد':<12} | {'قیمت':>10} | {'تغییر':>8} | {'حجم فروش':>15} | {'نوع':>10}")
        print("  " + "-" * 75)
        for q in queue_sell[:20]:
            print(f"  {q['symbol'][:12]:<12} | {int(q['price']):>10,} | {q['change']:>7.2f}% | {int(q['vol_sell']):>15,} | {q['type']:>10}")
    else:
        print("  ❌ صف فروش قوی نیست")
    print()

    print("=" * 100)
    print("  ✅ پایان")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
