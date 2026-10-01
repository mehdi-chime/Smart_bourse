# tomorrow_picks_v2.py
# پیشنهاد خرید + RSI + ATR
# اجرا: python tomorrow_picks_v2.py

import sys
import json
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np


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
        except:
            continue
    return None


def analyze_stock(row, with_rsi=True):
    """تحلیل یک سهم"""
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            return None

        last = float(row.get("Last") or row.get("Close") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)

        if last <= 0 or min_a <= 0 or max_a <= 0:
            return None

        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        total_vol = vol_buy + vol_sell
        if total_vol < 500_000:
            return None

        distance_from_min = (last - min_a) / min_a * 100
        if distance_from_min > 10:
            return None

        # RSI + ATR (اختیاری - کند هست)
        rsi = None
        atr_pct = None
        if with_rsi:
            hist = get_history_safe(symbol)
            if hist is not None:
                closes = hist["Close"].tolist()
                highs = hist["High"].tolist() if "High" in hist.columns else closes
                lows = hist["Low"].tolist() if "Low" in hist.columns else closes

                rsi = calc_rsi(closes, 14)
                atr_val = calc_atr(highs, lows, closes, 14)
                if atr_val and last > 0:
                    atr_pct = (atr_val / last * 100)

        # امتیازدهی
        score = 0
        reasons = []

        # ۱. فاصله از کف (25)
        if distance_from_min < 1:
            score += 25
            reasons.append("نزدیک کف")
        elif distance_from_min < 2:
            score += 20
            reasons.append("فاصله 2% از کف")
        elif distance_from_min < 3:
            score += 15
        elif distance_from_min < 5:
            score += 10

        # ۲. RSI (25)
        if rsi is not None:
            if rsi < 20:
                score += 25
                reasons.append(f"RSI خیلی پایین ({rsi})")
            elif rsi < 30:
                score += 20
                reasons.append(f"RSI پایین ({rsi})")
            elif rsi < 40:
                score += 15
                reasons.append(f"RSI مناسب ({rsi})")
            elif rsi < 50:
                score += 10
                reasons.append(f"RSI متوسط ({rsi})")
            elif rsi > 70:
                score -= 10
                reasons.append(f"⚠️ RSI بالا ({rsi})")

        # ۳. ATR (20)
        if atr_pct is not None:
            if atr_pct > 4:
                score += 20
                reasons.append(f"نوسان بالا (ATR {atr_pct:.1f}%)")
            elif atr_pct > 3:
                score += 15
                reasons.append(f"نوسان خوب (ATR {atr_pct:.1f}%)")
            elif atr_pct > 2.5:
                score += 10
            elif atr_pct < 1.5:
                score -= 5
                reasons.append(f"⚠️ نوسان کم (ATR {atr_pct:.1f}%)")

        # ۴. حقوقی (20)
        if vol_sell_n > 0:
            ratio_n = vol_buy_n / vol_sell_n
            if ratio_n > 5:
                score += 20
                reasons.append(f"حقوقی قوی ({ratio_n:.1f}x)")
            elif ratio_n > 3:
                score += 15
                reasons.append(f"حقوقی خریدار ({ratio_n:.1f}x)")
            elif ratio_n > 1.5:
                score += 10
            elif ratio_n > 1:
                score += 5
        elif vol_buy_n > 0:
            score += 15
            reasons.append("حقوقی فقط خریدار")

        # ۵. تغییر (10)
        if -3 < change < 0:
            score += 10
            reasons.append(f"منفی کم ({change:.2f}%)")
        elif 0 <= change < 1:
            score += 5
            reasons.append(f"نزدیک صفر ({change:.2f}%)")

        profit = (max_a / min_a - 1) * 100 - 1.25

        return {
            "symbol": symbol,
            "last": last,
            "yesterday": yesterday,
            "min_a": min_a,
            "max_a": max_a,
            "change": change,
            "distance_from_min": distance_from_min,
            "vol_buy": vol_buy,
            "vol_sell": vol_sell,
            "vol_buy_n": vol_buy_n,
            "vol_sell_n": vol_sell_n,
            "rsi": rsi,
            "atr_pct": atr_pct,
            "score": score,
            "profit": profit,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": min_a * 0.98,
            "reasons": reasons,
        }
    except:
        return None


def main():
    print()
    print("=" * 110)
    print(f"  🎯 پیشنهاد خرید برای فردا (v2 - با RSI/ATR)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)
    print()

    print("  📡 دریافت داده...")
    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  ✅ {len(df)} سهم")
    print()

    # مرحله ۱: فیلتر سریع (بدون RSI)
    print("  🔍 فیلتر سریع...")
    quick = []
    for _, row in df.iterrows():
        r = analyze_stock(row, with_rsi=False)
        if r:
            quick.append((r, row))

    print(f"  ✅ {len(quick)} کاندید اولیه")
    print()

    # مرحله ۲: RSI + ATR (فقط برای بهترین‌ها)
    quick.sort(key=lambda x: -x[0]["score"])
    top50 = quick[:50]

    print(f"  📊 محاسبه RSI + ATR برای {len(top50)} سهم برتر...")
    print()

    results = []
    for i, (r, row) in enumerate(top50, 1):
        symbol = r["symbol"]
        print(f"  [{i}/{len(top50)}] {symbol}", end=" ... ")

        full = analyze_stock(row, with_rsi=True)
        if full:
            results.append(full)
            rsi_str = f"RSI={full['rsi']}" if full['rsi'] else "RSI=?"
            atr_str = f"ATR={full['atr_pct']:.1f}%" if full['atr_pct'] else "ATR=?"
            print(f"OK ({rsi_str}, {atr_str}, امتیاز {full['score']})")
        else:
            print("skip")

    print()
    results.sort(key=lambda x: -x["score"])

    # نمایش
    print("=" * 110)
    print(f"  🏆 بهترین ۱۰ سهم برای فردا")
    print("=" * 110)
    print()

    print(f"  {'#':<3} | {'نماد':<10} | {'قیمت':>10} | {'تغییر':>8} | {'RSI':>5} | {'ATR%':>5} | {'امتیاز':>7} | {'سود':>6}")
    print("  " + "-" * 95)

    for i, s in enumerate(results[:10], 1):
        rsi_str = f"{s['rsi']:.1f}" if s['rsi'] else "—"
        atr_str = f"{s['atr_pct']:.1f}" if s['atr_pct'] else "—"

        print(
            f"  {i:<3} | "
            f"{s['symbol'][:10]:<10} | "
            f"{int(s['last']):>10,} | "
            f"{s['change']:>7.2f}% | "
            f"{rsi_str:>5} | "
            f"{atr_str:>5} | "
            f"{s['score']:>5}/100 | "
            f"{s['profit']:>5.2f}%"
        )

    print()

    # جزئیات
    print("=" * 110)
    print(f"  📊 جزئیات ۵ سهم برتر")
    print("=" * 110)
    print()

    for i, s in enumerate(results[:5], 1):
        print(f"  ── {i}. {s['symbol']} (امتیاز {s['score']}) ──")
        print(f"     💰 قیمت:  {int(s['last']):,} ({s['change']:+.2f}%)")
        if s['rsi']:
            print(f"     📊 RSI:   {s['rsi']}")
        if s['atr_pct']:
            print(f"     📊 ATR:   {s['atr_pct']:.2f}%")
        print(f"     📉 کف:    {int(s['min_a']):,}")
        print(f"     📈 سقف:   {int(s['max_a']):,}")
        print()
        print(f"     🟢 خرید:  {int(s['buy_target']):,}")
        print(f"     🔴 فروش:  {int(s['sell_target']):,}")
        print(f"     ⛔ حدضرر: {int(s['stop_loss']):,}")
        print(f"     💰 سود:   {s['profit']:.2f}%")
        print()
        print(f"     📊 دلایل:")
        for r in s['reasons']:
            print(f"        ✅ {r}")
        print()

    # ذخیره
    output = PROJECT_ROOT / "data" / "hunter" / f"tomorrow_v2_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "top": results[:20],
        }, f, ensure_ascii=False, indent=2)

    print("=" * 110)
    print(f"  💾 ذخیره: {output}")
    print("=" * 110)
    print()


if __name__ == "__main__":
    main()
