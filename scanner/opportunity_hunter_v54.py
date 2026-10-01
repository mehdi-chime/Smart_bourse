
# scanner/opportunity_hunter_v54.py
# Smart_Bourse - Opportunity Hunter v54
# اجرا: python scanner\opportunity_hunter_v54.py

import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import algotik_tse as att
except ImportError:
    print("❌ algotik_tse نصب نیست. بزن: pip install algotik-tse")
    sys.exit(1)

import numpy as np


# ═══════════════════════════════════════════════════════════
# تنظیمات v54
# ═══════════════════════════════════════════════════════════
RSI_MIN = 15           # ← از ۲۵ به ۱۵
RSI_MAX = 55
MIN_ATR_PCT = 2.5
MIN_VOLUME = 1_000_000  # ← از ۵۰۰K به ۱M
MIN_RATIO = 1.0
MAX_RATIO = 100        # فیلتر صف خرید
LOOKBACK = 120         # ← از ۶۰ به ۱۲۰

# مسیرها
DATA_DIR = PROJECT_ROOT / "data" / "hunter"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


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


def calc_atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    return float(np.mean(trs[-period:]))


def get_history_safe(symbol):
    for alias in [symbol, normalize(symbol)]:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 15:
                    return df
        except Exception:
            continue
    return None


def analyze_stock(symbol):
    df = get_history_safe(symbol)
    if df is None or df.empty:
        return None
    closes = df["Close"].tolist()
    if len(closes) < 15:
        return None
    closes = closes[-LOOKBACK:]
    highs = df["High"].tolist()[-LOOKBACK:] if "High" in df.columns else closes
    lows = df["Low"].tolist()[-LOOKBACK:] if "Low" in df.columns else closes
    last = closes[-1]
    rsi = calc_rsi(closes, 14)
    atr_val = calc_atr(highs, lows, closes, 14)
    atr_pct = (atr_val / last * 100) if atr_val and last > 0 else 0
    support = min(closes[-20:]) if len(closes) >= 20 else min(closes)
    resistance = max(closes[-20:]) if len(closes) >= 20 else max(closes)
    return {
        "symbol": symbol, "price": last, "rsi": rsi,
        "atr": atr_val, "atr_pct": atr_pct,
        "support": support, "resistance": resistance,
    }


def send_to_eitaa(text):
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "eitaa"))
        from eitaa_bot import EitaaBot
        bot = EitaaBot()
        bot.send_message(text)
        return True
    except Exception as e:
        print(f"  [ایتا] خطا: {e}")
        return False


def main():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    print()
    print("=" * 100)
    print(f"  Smart_Bourse - Opportunity Hunter v54")
    print(f"  {date_str} {time_str}")
    print("=" * 100)
    print(f"  استراتژی: خرید -3٪ / فروش +3٪ / حد ضرر -5٪")
    print(f"  فیلتر: RSI {RSI_MIN}-{RSI_MAX} | ATR > {MIN_ATR_PCT}% | حجم > {MIN_VOLUME:,}")
    print()

    print("دریافت داده از TSETMC...")
    df = att.get_live_market()
    if df is None or df.empty:
        print("❌ خطا در دریافت داده")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  کل سهام: {len(df)}")
    print()

    candidates = []
    for _, row in df.iterrows():
        try:
            symbol = str(row.get("Symbol", ""))
            if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
                continue
            last = float(row.get("Last") or row.get("Close") or 0)
            if last <= 0:
                continue
            vol_buy = float(row.get("Vol_buy_retail") or 0)
            vol_sell = float(row.get("Vol_sell_retail") or 0)
            if vol_sell > 0:
                ratio = vol_buy / vol_sell
            elif vol_buy > 0:
                ratio = 9999
            else:
                ratio = 0
            if ratio < MIN_RATIO or ratio > MAX_RATIO:
                continue
            total_vol = vol_buy + vol_sell
            if total_vol < MIN_VOLUME:
                continue
            candidates.append({
                "symbol": symbol, "price": last,
                "change": float(row.get("ChangePct") or 0),
                "ratio": ratio, "vol_buy": vol_buy, "vol_sell": vol_sell,
            })
        except Exception:
            continue

    print(f"  کاندیدهای اولیه: {len(candidates)}")
    print("محاسبه RSI و ATR...")
    print()

    results = []
    for i, c in enumerate(candidates, 1):
        symbol = c["symbol"]
        print(f"  [{i}/{len(candidates)}] {symbol}", end=" ... ")
        data = analyze_stock(symbol)
        if data is None:
            print("skip")
            continue
        rsi = data.get("rsi")
        atr_pct = data.get("atr_pct", 0)
        if rsi is None:
            print("no RSI")
            continue
        if not (RSI_MIN <= rsi <= RSI_MAX):
            print(f"RSI {rsi}")
            continue
        if atr_pct < MIN_ATR_PCT:
            print(f"ATR {round(atr_pct, 1)}%")
            continue
        results.append({
            "symbol": symbol, "price": data["price"],
            "change": c["change"], "ratio": round(c["ratio"], 2),
            "rsi": rsi, "atr_pct": round(atr_pct, 2),
            "support": round(data["support"], 0),
            "resistance": round(data["resistance"], 0),
            "buy_target": round(data["price"] * 0.97, 0),
            "sell_target": round(data["price"] * 1.03, 0),
            "stop_loss": round(data["price"] * 0.95, 0),
        })
        print("OK")

    print()
    print("=" * 100)
    print("  🎯 فرصت‌های مناسب")
    print("=" * 100)
    print()

    if not results:
        print("  ❌ هیچ سهمی پیدا نشد.")
        return

    results.sort(key=lambda x: x["rsi"])

    print("  " + "نماد".ljust(12) + " | " + "قیمت".rjust(10) + " | " + "RSI".rjust(5) + " | " + "ATR%".rjust(5) + " | " + "نسبت".rjust(6) + " | " + "خرید".rjust(10) + " | " + "فروش".rjust(10) + " | " + "حدضرر".rjust(10))
    print("  " + "-" * 95)
    for r in results[:30]:
        print(
            "  " + r["symbol"][:12].ljust(12)
            + " | " + "{:,}".format(int(r["price"])).rjust(10)
            + " | " + str(r["rsi"]).rjust(5)
            + " | " + "{:.1f}".format(r["atr_pct"]).rjust(5)
            + " | " + "{:.2f}".format(r["ratio"]).rjust(6)
            + " | " + "{:,}".format(int(r["buy_target"])).rjust(10)
            + " | " + "{:,}".format(int(r["sell_target"])).rjust(10)
            + " | " + "{:,}".format(int(r["stop_loss"])).rjust(10)
        )
    print()
    print(f"  تعداد فرصت‌ها: {len(results)}")
    print()

    # ذخیره JSON
    json_path = DATA_DIR / f"hunter_{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str, "time": time_str,
            "settings": {
                "RSI_MIN": RSI_MIN, "RSI_MAX": RSI_MAX,
                "MIN_ATR_PCT": MIN_ATR_PCT, "MIN_VOLUME": MIN_VOLUME,
                "LOOKBACK": LOOKBACK,
            },
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"  ✅ ذخیره JSON: {json_path}")

    # ذخیره گزارش
    report_path = REPORTS_DIR / f"hunter_{date_str}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Opportunity Hunter v54 - {date_str} {time_str}\n")
        f.write("=" * 80 + "\n\n")
        for r in results:
            f.write(f"{r['symbol']}\n")
            f.write(f"  قیمت: {int(r['price']):,}\n")
            f.write(f"  RSI: {r['rsi']} | ATR: {r['atr_pct']}% | نسبت: {r['ratio']}\n")
            f.write(f"  خرید: {int(r['buy_target']):,}\n")
            f.write(f"  فروش: {int(r['sell_target']):,}\n")
            f.write(f"  حد ضرر: {int(r['stop_loss']):,}\n\n")
    print(f"  ✅ ذخیره گزارش: {report_path}")

    # ارسال به ایتا
    if results:
        text = f"🎯 فرصت‌های {date_str}\n\n"
        for r in results[:10]:
            text += f"📌 {r['symbol']}\n"
            text += f"   قیمت: {int(r['price']):,}\n"
            text += f"   خرید: {int(r['buy_target']):,} | فروش: {int(r['sell_target']):,}\n"
            text += f"   RSI: {r['rsi']}\n\n"
        if send_to_eitaa(text):
            print("  ✅ ارسال به ایتا")

    print()
    print("=" * 100)
    print("  ✅ تمام شد!")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
