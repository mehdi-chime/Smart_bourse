# adaptive_strategy.py
# استراتژی تطبیقی بر اساس وضعیت بازار
# اجرا: python adaptive_strategy.py

import sys
import json
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

HUNTER_DIR = PROJECT_ROOT / "data" / "hunter"


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


def get_market_status():
    """وضعیت بازار"""
    df = att.get_live_market()
    if df is None or df.empty:
        return None, 0

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    positive = 0
    negative = 0
    total = 0

    for _, row in df.iterrows():
        try:
            change = float(row.get("ChangePct") or 0)
            total += 1
            if change > 0:
                positive += 1
            elif change < 0:
                negative += 1
        except:
            continue

    if total == 0:
        return None, 0

    pos_pct = positive / total * 100

    if pos_pct > 70:
        return "🟢 سبز قوی", pos_pct
    elif pos_pct > 55:
        return "🟢 سبز", pos_pct
    elif pos_pct > 45:
        return "🟡 متعادل", pos_pct
    elif pos_pct > 30:
        return "🔴 قرمز", pos_pct
    else:
        return "🔴 قرمز شدید", pos_pct


def get_adaptive_target(market_status):
    """هدف تطبیقی"""
    if "سبز قوی" in market_status:
        return 0.0
    elif "سبز" in market_status:
        return -1.0
    elif "متعادل" in market_status:
        return -2.0
    elif "قرمز" in market_status:
        return -3.0
    else:
        return -4.0


def main():
    print()
    print("=" * 100)
    print(f"  🎯 استراتژی تطبیقی")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()

    # وضعیت بازار
    print("  📊 بررسی وضعیت بازار...")
    market_status, pos_pct = get_market_status() or ("نامشخص", 0)
    print(f"     وضعیت: {market_status} ({pos_pct:.1f}% مثبت)")
    print()

    # هدف تطبیقی
    target_pct = get_adaptive_target(market_status)
    print(f"  🎯 هدف خرید: {target_pct:+.1f}%")
    print()
    print(f"  💡 چرا؟")
    if target_pct == 0:
        print(f"     بازار سبز قوی → صفر تابلو بخر")
    elif target_pct == -1:
        print(f"     بازار سبز → -1% بخر")
    elif target_pct == -2:
        print(f"     بازار متعادل → -2% بخر")
    elif target_pct == -3:
        print(f"     بازار قرمز → -3% بخر")
    else:
        print(f"     بازار قرمز شدید → -4% بخر")
    print()

    # خواندن hunter
    hunter_files = sorted(HUNTER_DIR.glob("hunter_*.json"))
    if not hunter_files:
        print("  ❌ فایل hunter پیدا نشد")
        return

    latest = hunter_files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    print(f"  📊 {len(results)} سهم از hunter")
    print()

    # محاسبه اهداف جدید
    print("=" * 100)
    print(f"  🎯 اهداف جدید (خرید {target_pct:+.1f}% / فروش +3%)")
    print("=" * 100)
    print()

    print(f"  {'#':<3} | {'نماد':<12} | {'قیمت':>10} | {'خرید جدید':>12} | {'فروش':>10} | {'RSI':>5} | {'سود':>6}")
    print("  " + "-" * 85)

    for i, r in enumerate(results[:20], 1):
        price = r["price"]
        new_buy = round(price * (1 + target_pct / 100), 0)
        new_sell = round(price * 1.03, 0)
        rsi = r["rsi"]

        # سود انتظاری
        profit = (new_sell / new_buy - 1) * 100 - 1.25

        print(
            f"  {i:<3} | "
            f"{r['symbol'][:12]:<12} | "
            f"{int(price):>10,} | "
            f"{int(new_buy):>12,} | "
            f"{int(new_sell):>10,} | "
            f"{rsi:>5} | "
            f"{profit:>5.2f}%"
        )

    print()
    print("=" * 100)
    print(f"  ✅ استراتژی: خرید {target_pct:+.1f}% / فروش +3%")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
