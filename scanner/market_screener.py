
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np


SAFE_BUY_RATIO = 3.0      # نسبت خرید/فروش حقیقی
SAFE_SELL_RATIO = 0.3     # نسبت فروش/خرید حقیقی
MIN_VOLUME = 100_000      # حداقل حجم


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


def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    p = np.array(prices, dtype=float)
    deltas = np.diff(p)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    ag = gains[-period:].mean()
    al = losses[-period:].mean()
    if al == 0 and ag > 0:
        return 100
    if al == 0 and ag == 0:
        return 50
    rs = ag / al
    return round(100 - (100 / (1 + rs)), 1)


def get_rsi_safe(symbol):
    """گرفتن RSI با تلاش چند باره"""
    for alias in [symbol, normalize(symbol)]:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 15:
                    return calc_rsi(df["Close"].tolist()[-60:], 14)
        except Exception:
            continue
    return None


def main():
    print()
    print("=" * 90)
    print("  Smart_Bourse - Market Screener")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 90)
    print()

    # 1. دریافت داده
    print("دریافت داده از TSETMC...")
    df = att.get_live_market()
    if df is None or df.empty:
        print("خطا: داده‌ای نیومد")
        return

    # فقط سهام عادی
    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    total = len(df)
    print("کل سهم‌ها: " + str(total))
    print()

    # 2. محاسبه نسبت
    results = []
    for _, row in df.iterrows():
        try:
            symbol = str(row.get("Symbol", ""))
            if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
                continue

            price = float(row.get("Last") or row.get("Close") or 0)
            change = float(row.get("ChangePct") or 0)
            vol_buy = float(row.get("Vol_buy_retail") or 0)
            vol_sell = float(row.get("Vol_sell_retail") or 0)

            if vol_sell > 0:
                ratio = vol_buy / vol_sell
            elif vol_buy > 0:
                ratio = 9999
            else:
                continue

            total_vol = vol_buy + vol_sell
            if total_vol < MIN_VOLUME:
                continue

            results.append({
                "symbol": symbol,
                "price": price,
                "change": change,
                "ratio": ratio,
                "vol_buy": vol_buy,
                "vol_sell": vol_sell,
            })
        except Exception:
            continue

    print("سهم‌های معتبر: " + str(len(results)))
    print()

    # 3. جدا کردن SAFE_BUY
    safe_buy = [r for r in results if r["ratio"] >= SAFE_BUY_RATIO]
    safe_sell = [r for r in results if r["ratio"] <= SAFE_SELL_RATIO]

    # مرتب‌سازی
    safe_buy.sort(key=lambda x: x["ratio"], reverse=True)
    safe_sell.sort(key=lambda x: x["ratio"])

    # 4. محاسبه RSI برای SAFE_BUY
    print("محاسبه RSI برای " + str(len(safe_buy)) + " سهم...")
    for r in safe_buy:
        r["rsi"] = get_rsi_safe(r["symbol"])
    print()

    # 5. نمایش SAFE_BUY
    print("=" * 90)
    print("  SAFE BUY (نسبت خرید/فروش >= " + str(SAFE_BUY_RATIO) + ")")
    print("=" * 90)
    print()
    print("  " + "نماد".ljust(12) + " | " + "قیمت".rjust(8) + " | " + "تغییر".rjust(8) + " | " + "نسبت".rjust(7) + " | " + "RSI".rjust(6) + " | " + "وضعیت")
    print("  " + "-" * 78)

    for r in safe_buy[:40]:  # حداکثر ۴۰
        rsi = r.get("rsi")
        rsi_str = str(rsi) if rsi else "?"

        # وضعیت RSI
        if rsi is None:
            status = "?"
        elif rsi >= 80:
            status = "⚠️ اشباع خرید"
        elif rsi >= 70:
            status = "⚠️ بالا"
        elif rsi >= 55:
            status = "نرمال+"
        elif rsi >= 45:
            status = "نرمال"
        elif rsi >= 30:
            status = "🟢 پایین"
        else:
            status = "🟢🟢 اشباع فروش"

        change_str = "{:+.2f}%".format(r["change"])
        print(
            "  " + r["symbol"][:12].ljust(12)
            + " | " + "{:,}".format(int(r["price"])).rjust(8)
            + " | " + change_str.rjust(8)
            + " | " + "{:.2f}".format(r["ratio"]).rjust(7)
            + " | " + rsi_str.rjust(6)
            + " | " + status
        )

    print()

    # 6. نمایش SAFE_SELL
    print("=" * 90)
    print("  SAFE SELL (نسبت خرید/فروش <= " + str(SAFE_SELL_RATIO) + ")")
    print("=" * 90)
    print()
    print("  " + "نماد".ljust(12) + " | " + "قیمت".rjust(8) + " | " + "تغییر".rjust(8) + " | " + "نسبت".rjust(7))
    print("  " + "-" * 58)

    for r in safe_sell[:30]:
        change_str = "{:+.2f}%".format(r["change"])
        print(
            "  " + r["symbol"][:12].ljust(12)
            + " | " + "{:,}".format(int(r["price"])).rjust(8)
            + " | " + change_str.rjust(8)
            + " | " + "{:.2f}".format(r["ratio"]).rjust(7)
        )

    print()

    # 7. خلاصه
    print("=" * 90)
    print("  خلاصه")
    print("=" * 90)
    print("  SAFE_BUY:  " + str(len(safe_buy)) + " سهم")
    print("  SAFE_SELL: " + str(len(safe_sell)) + " سهم")
    print("  کل بازار:   " + str(len(results)) + " سهم")
    print()

    # 8. بهترین‌ها
    if safe_buy:
        # فقط اونایی که RSI < 60
        best = [r for r in safe_buy if r.get("rsi") and r["rsi"] < 60]
        if best:
            print("=" * 90)
            print("  ⭐ بهترین فرصت‌ها (RSI < 60 + نسبت بالا)")
            print("=" * 90)
            print()
            for r in best[:10]:
                print("  " + r["symbol"][:15].ljust(15)
                      + " | نسبت: " + "{:.2f}".format(r["ratio"]).rjust(6)
                      + " | RSI: " + str(r["rsi"]).rjust(5)
                      + " | قیمت: " + "{:,}".format(int(r["price"])))
            print()
        else:
            print("  ⚠️  هیچ سهمی با RSI < 60 پیدا نشد (بازار اشباع خریده)")
            print()

    print("=" * 90)
    print("  " + datetime.now().strftime("%H:%M:%S"))
    print("=" * 90)
    print()


if __name__ == "__main__":
    main()
