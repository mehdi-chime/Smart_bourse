# analyze_top_signals.py
# تحلیل و امتیازدهی همه سهم‌های hunter
# اجرا: python analyze_top_signals.py

import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import algotik_tse as att
except ImportError:
    print("❌ algotik_tse نصب نیست")
    sys.exit(1)

import numpy as np


# ═══════════════════════════════════════════════════════════
# تنظیمات امتیازدهی
# ═══════════════════════════════════════════════════════════
LOOKBACK = 120
TOP_N = 10

# وزن‌ها (جمعاً ۱۰۰)
WEIGHT_RSI = 30
WEIGHT_ATR = 20
WEIGHT_TREND = 20
WEIGHT_RESISTANCE = 15
WEIGHT_VOLUME = 15


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


def calc_ma(prices, period):
    if len(prices) < period:
        return None
    return float(np.mean(prices[-period:]))


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


def analyze_and_score(symbol, live_data):
    df = get_history_safe(symbol)
    if df is None or df.empty:
        return None

    closes = df["Close"].tolist()
    if len(closes) < 20:
        return None

    closes = closes[-LOOKBACK:]
    highs = df["High"].tolist()[-LOOKBACK:] if "High" in df.columns else closes
    lows = df["Low"].tolist()[-LOOKBACK:] if "Low" in df.columns else closes

    last = closes[-1]
    rsi = calc_rsi(closes, 14)
    atr_val = calc_atr(highs, lows, closes, 14)
    atr_pct = (atr_val / last * 100) if atr_val and last > 0 else 0

    ma5 = calc_ma(closes, 5)
    ma20 = calc_ma(closes, 20)
    ma50 = calc_ma(closes, 50)

    support_20 = min(closes[-20:])
    resistance_20 = max(closes[-20:])
    resistance_60 = max(closes[-60:]) if len(closes) >= 60 else max(closes)

    change_20d = ((closes[-1] - closes[-21]) / closes[-21] * 100) if len(closes) >= 21 else 0

    # روند
    if ma5 and ma20 and ma50:
        if ma5 > ma20 > ma50:
            trend = "صعودی"
            trend_score = WEIGHT_TREND
        elif ma5 < ma20 < ma50:
            trend = "نزولی"
            trend_score = 0
        else:
            trend = "خنثی"
            trend_score = WEIGHT_TREND * 0.5
    else:
        trend = "نامشخص"
        trend_score = 0

    # ═══════════════════════════════════════════════════════
    # امتیازدهی
    # ═══════════════════════════════════════════════════════

    # ۱. RSI (۳۰ نمره)
    if rsi is None:
        rsi_score = 0
    elif 15 <= rsi <= 35:
        rsi_score = WEIGHT_RSI       # بهترین
    elif 35 < rsi <= 45:
        rsi_score = WEIGHT_RSI * 0.8
    elif 45 < rsi <= 55:
        rsi_score = WEIGHT_RSI * 0.5
    elif rsi < 15:
        rsi_score = WEIGHT_RSI * 0.6
    else:
        rsi_score = 0

    # ۲. ATR (۲۰ نمره)
    if atr_pct >= 4:
        atr_score = WEIGHT_ATR
    elif atr_pct >= 3:
        atr_score = WEIGHT_ATR * 0.8
    elif atr_pct >= 2.5:
        atr_score = WEIGHT_ATR * 0.5
    else:
        atr_score = 0

    # ۳. فاصله تا مقاومت (۱۵ نمره)
    if resistance_60 > 0:
        distance_to_resistance = (resistance_60 - last) / last * 100
    else:
        distance_to_resistance = 0

    if distance_to_resistance >= 10:
        resistance_score = WEIGHT_RESISTANCE
    elif distance_to_resistance >= 5:
        resistance_score = WEIGHT_RESISTANCE * 0.7
    elif distance_to_resistance >= 3:
        resistance_score = WEIGHT_RESISTANCE * 0.4
    else:
        resistance_score = 0

    # ۴. حجم (۱۵ نمره)
    total_vol = live_data.get("vol_buy", 0) + live_data.get("vol_sell", 0)
    if total_vol >= 10_000_000:
        volume_score = WEIGHT_VOLUME
    elif total_vol >= 5_000_000:
        volume_score = WEIGHT_VOLUME * 0.8
    elif total_vol >= 1_000_000:
        volume_score = WEIGHT_VOLUME * 0.5
    else:
        volume_score = 0

    total_score = rsi_score + atr_score + trend_score + resistance_score + volume_score

    return {
        "symbol": symbol,
        "price": last,
        "rsi": rsi,
        "atr_pct": round(atr_pct, 2),
        "trend": trend,
        "distance_to_resistance": round(distance_to_resistance, 1),
        "change_20d": round(change_20d, 1),
        "total_vol": total_vol,
        "score": round(total_score, 1),
        "rsi_score": round(rsi_score, 1),
        "atr_score": round(atr_score, 1),
        "trend_score": round(trend_score, 1),
        "resistance_score": round(resistance_score, 1),
        "volume_score": round(volume_score, 1),
        "buy_target": round(last * 0.97, 0),
        "sell_target": round(last * 1.03, 0),
        "stop_loss": round(last * 0.97 * 0.98, 0),
    }


def main():
    date_str = datetime.now().strftime("%Y-%m-%d")

    print()
    print("=" * 100)
    print(f"  🎯 Smart_Bourse - تحلیل و امتیازدهی سهم‌ها")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()

    # ۱. خواندن آخرین hunter JSON
    hunter_dir = PROJECT_ROOT / "data" / "hunter"
    json_files = sorted(hunter_dir.glob("hunter_*.json"))

    if not json_files:
        print("❌ هیچ فایل hunter پیدا نشد!")
        print("   اول اجرا کن: python scanner\\opportunity_hunter_v54.py")
        return

    latest = json_files[-1]
    print(f"  📁 آخرین فایل: {latest.name}")

    with open(latest, "r", encoding="utf-8") as f:
        hunter_data = json.load(f)

    symbols = hunter_data.get("results", [])
    print(f"  📊 تعداد سهم‌ها: {len(symbols)}")
    print()

    # ۲. دریافت داده زنده
    print("  دریافت داده زنده از TSETMC...")
    try:
        live_df = att.get_live_market()
        if "InstrumentType" in live_df.columns:
            live_df = live_df[live_df["InstrumentType"] == 300]
    except Exception as e:
        print(f"  ⚠️ خطا: {e}")
        live_df = None

    # ۳. تحلیل و امتیازدهی
    print("  محاسبه امتیاز...")
    print()

    results = []
    for i, s in enumerate(symbols, 1):
        symbol = s["symbol"]
        print(f"  [{i}/{len(symbols)}] {symbol}", end=" ... ")

        # داده زنده برای این سهم
        live_data = {}
        if live_df is not None:
            try:
                row = live_df[live_df["Symbol"] == symbol]
                if not row.empty:
                    r = row.iloc[0]
                    live_data = {
                        "vol_buy": float(r.get("Vol_buy_retail") or 0),
                        "vol_sell": float(r.get("Vol_sell_retail") or 0),
                    }
            except Exception:
                pass

        r = analyze_and_score(symbol, live_data)
        if r is None:
            print("skip")
            continue

        results.append(r)
        print(f"{r['score']}/100")

    # ۴. مرتب‌سازی بر اساس امتیاز
    results.sort(key=lambda x: -x["score"])

    # ۵. نمایش
    print()
    print("=" * 100)
    print(f"  🏆 بهترین {TOP_N} سهم برای فردا")
    print("=" * 100)
    print()

    print(f"  {'#':<3} | {'نماد':<10} | {'قیمت':>10} | {'RSI':>5} | {'ATR%':>5} | {'روند':<8} | {'فاصله':>7} | {'امتیاز':>7}")
    print("  " + "-" * 85)

    for i, r in enumerate(results[:TOP_N], 1):
        print(
            f"  {i:<3} | "
            f"{r['symbol'][:10]:<10} | "
            f"{int(r['price']):>10,} | "
            f"{str(r['rsi']):>5} | "
            f"{r['atr_pct']:>5.1f} | "
            f"{r['trend']:<8} | "
            f"{r['distance_to_resistance']:>6.1f}% | "
            f"{r['score']:>5.1f}/100"
        )

    print()

    # ۶. جدول معاملات
    print("=" * 100)
    print(f"  🎯 جدول معاملات برای {TOP_N} سهم برتر")
    print("=" * 100)
    print()

    print(f"  {'نماد':<10} | {'قیمت':>10} | {'خرید':>10} | {'فروش':>10} | {'حدضرر':>10} | {'سود':>6}")
    print("  " + "-" * 75)

    for r in results[:TOP_N]:
        profit = (r['sell_target'] / r['buy_target'] - 1) * 100 - 1.25
        print(
            f"  {r['symbol'][:10]:<10} | "
            f"{int(r['price']):>10,} | "
            f"{int(r['buy_target']):>10,} | "
            f"{int(r['sell_target']):>10,} | "
            f"{int(r['stop_loss']):>10,} | "
            f"{profit:>5.2f}%"
        )

    print()

    # ۷. تحلیل جزئیات ۳ سهم برتر
    print("=" * 100)
    print(f"  📊 تحلیل جزئیات ۳ سهم برتر")
    print("=" * 100)

    for i, r in enumerate(results[:3], 1):
        print()
        print(f"  ── {i}. {r['symbol']} ──")
        print(f"     💰 قیمت: {int(r['price']):,}")
        print(f"     🔵 RSI: {r['rsi']} ({r['rsi_score']:.1f}/{WEIGHT_RSI})")
        print(f"     🔵 ATR: {r['atr_pct']}% ({r['atr_score']:.1f}/{WEIGHT_ATR})")
        print(f"     📊 روند: {r['trend']} ({r['trend_score']:.1f}/{WEIGHT_TREND})")
        print(f"     📈 فاصله تا مقاومت: {r['distance_to_resistance']}% ({r['resistance_score']:.1f}/{WEIGHT_RESISTANCE})")
        print(f"     📊 حجم: {int(r['total_vol']):,} ({r['volume_score']:.1f}/{WEIGHT_VOLUME})")
        print(f"     📉 تغییر ۲۰ روز: {r['change_20d']}%")
        print(f"     🎯 امتیاز کل: {r['score']}/100")
        print(f"     💡 خرید: {int(r['buy_target']):,} | فروش: {int(r['sell_target']):,} | حدضرر: {int(r['stop_loss']):,}")

    # ۸. ذخیره
    output_file = PROJECT_ROOT / "data" / "hunter" / f"scores_{date_str}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "total_symbols": len(results),
            "top": results[:TOP_N],
            "all": results,
        }, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 100)
    print(f"  ✅ ذخیره: {output_file}")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
