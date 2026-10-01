# a# strategy_50m.py
# استراتژی ۵۰ میلیون
# اجرا: python strategy_50m.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np

CAPITAL = 50_000_000  # 50 میلیون تومان = 500 میلیون ریال


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


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


def analyze_stock(row, layer):
    """تحلیل سهم برای هر لایه"""
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            return None

        last = float(row.get("Last") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0 or min_a <= 0 or max_a <= 0 or eps <= 0:
            return None

        pe = last / eps

        # فیلترهای هر لایه
        if layer == "safe":
            if pe > 10:
                return None
            max_rsi = 30
        elif layer == "medium":
            if pe > 15:
                return None
            max_rsi = 40
        elif layer == "aggressive":
            if pe > 15:
                return None
            max_rsi = 20

        # حجم
        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        if vol_buy + vol_sell < 500_000:
            return None

        # صف فروش (برای تهاجمی خوبه، برای امن بده)
        bid_v1 = float(row.get("BidVolume1") or 0)
        ask_v1 = float(row.get("AskVolume1") or 0)

        # RSI + ATR
        hist = get_history_safe(symbol)
        if hist is None:
            return None

        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        rsi = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)

        if rsi is None or atr_val is None:
            return None
        if rsi > max_rsi:
            return None

        atr_pct = (atr_val / last * 100) if last > 0 else 0
        if atr_pct < 2.5:
            return None

        # سود
        profit = (max_a / min_a - 1) * 100 - 1.25
        if profit < 3.5:
            return None

        # حقوقی
        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        # امتیاز
        score = 0

        # RSI (30)
        if rsi < 15:
            score += 30
        elif rsi < 20:
            score += 25
        elif rsi < 25:
            score += 20
        elif rsi < 30:
            score += 15
        elif rsi < 40:
            score += 10

        # P/E (25)
        if pe < 3:
            score += 25
        elif pe < 5:
            score += 20
        elif pe < 8:
            score += 15
        elif pe < 12:
            score += 10
        elif pe < 15:
            score += 5

        # حقوقی (25)
        if vol_sell_n > 0:
            ratio = vol_buy_n / vol_sell_n
            if ratio > 3:
                score += 25
            elif ratio > 1.5:
                score += 20
            elif ratio > 1:
                score += 10
        elif vol_buy_n > 0:
            score += 15

        # ATR (20)
        if atr_pct > 4.5:
            score += 20
        elif atr_pct > 4:
            score += 15
        elif atr_pct > 3:
            score += 10
        elif atr_pct > 2.5:
            score += 5

        return {
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "min_a": min_a,
            "max_a": max_a,
            "eps": eps,
            "pe": round(pe, 2),
            "rsi": rsi,
            "atr_pct": round(atr_pct, 2),
            "score": score,
            "profit": profit,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": round(min_a * 0.98),
        }
    except:
        return None


def main():
    print()
    print("=" * 110)
    print(f"  STRATEGY 50M - استراتژی ۵۰ میلیون")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)
    print()

    print(f"  Capital: {CAPITAL:,} rials = {CAPITAL//10:,} toman")
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ERR")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  OK: {len(df)} sahm")
    print()

    # ۳ لایه
    layers = {
        "safe": {"name": "امن", "pct": 0.4},
        "medium": {"name": "متوسط", "pct": 0.4},
        "aggressive": {"name": "تهاجمی", "pct": 0.2},
    }

    all_results = {}

    for layer_key, layer_info in layers.items():
        print(f"  Tahghigh laye {layer_info['name']} ({layer_info['pct']*100:.0f}%)...")
        results = []
        for _, row in df.iterrows():
            r = analyze_stock(row, layer_key)
            if r:
                results.append(r)

        results.sort(key=lambda x: -x["score"])
        all_results[layer_key] = results[:3]
        print(f"     {len(results)} candidate")

    print()

    # نمایش
    for layer_key, top_stocks in all_results.items():
        layer_info = layers[layer_key]
        capital_layer = CAPITAL * layer_info["pct"]
        per_stock = capital_layer / len(top_stocks) if top_stocks else 0

        print("=" * 110)
        print(f"  LAYE {layer_info['name']} ({layer_info['pct']*100:.0f}% = {capital_layer/10:,.0f} toman)")
        print("=" * 110)
        print()

        if not top_stocks:
            print("  Hich sahm")
            print()
            continue

        print(f"  {'#':<3} | {'Namad':<10} | {'Gheymat':>10} | {'PE':>5} | {'RSI':>5} | {'ATR':>5} | {'Emtiaz':>6} | {'Sood':>6} | {'Sarmaye':>12}")
        print("  " + "-" * 110)

        for i, s in enumerate(top_stocks, 1):
            # تعداد سهم
            qty = int(per_stock / s['last']) if s['last'] > 0 else 0
            actual = qty * s['last']

            print(
                f"  {i:<3} | "
                f"{s['symbol'][:10]:<10} | "
                f"{int(s['last']):>10,} | "
                f"{s['pe']:>5.1f} | "
                f"{s['rsi']:>5} | "
                f"{s['atr_pct']:>4.1f}% | "
                f"{s['score']:>4}/100 | "
                f"{s['profit']:>5.2f}% | "
                f"{actual/10:>10,.0f}T ({qty:,})"
            )
        print()

    # ذخیره
    output = PROJECT_ROOT / "data" / "hunter" / f"strategy_50m_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "capital": CAPITAL,
            "layers": all_results,
        }, f, ensure_ascii=False, indent=2)

    print("=" * 110)
    print(f"  Save: {output}")
    print("=" * 110)
    print()


if __name__ == "__main__":
    main()nalyze_foolad_khegostar.py
# تحلیل فولاد مبارکه و خگستر
# اجرا: python analyze_foolad_khegostar.py

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import algotik_tse as att
except ImportError:
    print("❌ algotik_tse نصب نیست")
    sys.exit(1)

import numpy as np
from datetime import datetime


SYMBOLS = ["فولاد", "خگستر"]
LOOKBACK = 120


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


def analyze(symbol):
    print()
    print("=" * 80)
    print(f"  📊 تحلیل {symbol}")
    print("=" * 80)

    df = get_history_safe(symbol)
    if df is None or df.empty:
        print(f"  ❌ داده‌ای برای {symbol} پیدا نشد")
        return None

    print(f"  تعداد کندل: {len(df)}")
    if hasattr(df.index, '__getitem__') and len(df.index) > 0:
        print(f"  از: {df.index[0]}")
        print(f"  تا: {df.index[-1]}")

    closes = df["Close"].tolist()
    highs = df["High"].tolist() if "High" in df.columns else closes
    lows = df["Low"].tolist() if "Low" in df.columns else closes
    volumes = df["Volume"].tolist() if "Volume" in df.columns else [0] * len(closes)

    # آخرین کندل
    last = closes[-1]
    last_high = highs[-1]
    last_low = lows[-1]
    last_vol = volumes[-1]

    # اندیکاتورها
    rsi = calc_rsi(closes, 14)
    atr_val = calc_atr(highs, lows, closes, 14)
    atr_pct = (atr_val / last * 100) if atr_val and last > 0 else 0

    # میانگین‌های متحرک
    ma5 = calc_ma(closes, 5)
    ma20 = calc_ma(closes, 20)
    ma50 = calc_ma(closes, 50)
    ma120 = calc_ma(closes, min(120, len(closes)))

    # سطوح کلیدی
    support_20 = min(closes[-20:]) if len(closes) >= 20 else min(closes)
    resistance_20 = max(closes[-20:]) if len(closes) >= 20 else max(closes)
    support_60 = min(closes[-60:]) if len(closes) >= 60 else min(closes)
    resistance_60 = max(closes[-60:]) if len(closes) >= 60 else max(closes)

    # تغییرات
    change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
    change_5d = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
    change_20d = ((closes[-1] - closes[-21]) / closes[-21] * 100) if len(closes) >= 21 else 0

    # روند
    if ma5 and ma20 and ma50:
        if ma5 > ma20 > ma50:
            trend = "🟢 صعودی"
        elif ma5 < ma20 < ma50:
            trend = "🔴 نزولی"
        else:
            trend = "🟡 خنثی"
    else:
        trend = "❓ نامشخص"

    # نمایش
    print()
    print(f"  💰 قیمت فعلی:        {int(last):,}")
    print(f"  📈 بالاترین امروز:   {int(last_high):,}")
    print(f"  📉 پایین‌ترین امروز:  {int(last_low):,}")
    print(f"  📊 حجم امروز:        {int(last_vol):,}")
    print()
    print(f"  🔵 RSI (14):         {rsi}")
    print(f"  🔵 ATR (14):         {int(atr_val):,}  ({atr_pct:.2f}%)")
    print()
    print(f"  📊 MA5:              {int(ma5):,}" if ma5 else "  📊 MA5:              -")
    print(f"  📊 MA20:             {int(ma20):,}" if ma20 else "  📊 MA20:             -")
    print(f"  📊 MA50:             {int(ma50):,}" if ma50 else "  📊 MA50:             -")
    print(f"  📊 MA120:            {int(ma120):,}" if ma120 else "  📊 MA120:            -")
    print()
    print(f"  🎯 روند:             {trend}")
    print()
    print(f"  📉 حمایت ۲۰ روز:     {int(support_20):,}")
    print(f"  📈 مقاومت ۲۰ روز:    {int(resistance_20):,}")
    print(f"  📉 حمایت ۶۰ روز:     {int(support_60):,}")
    print(f"  📈 مقاومت ۶۰ روز:    {int(resistance_60):,}")
    print()
    print(f"  📊 تغییر ۱ روز:      {change_1d:+.2f}%")
    print(f"  📊 تغییر ۵ روز:      {change_5d:+.2f}%")
    print(f"  📊 تغییر ۲۰ روز:     {change_20d:+.2f}%")
    print()

    # تحلیل استراتژی -3%/+3%
    buy_target = round(last * 0.97, 0)
    sell_target = round(last * 1.03, 0)
    stop_loss = round(buy_target * 0.98, 0)

    print("=" * 80)
    print(f"  🎯 استراتژی -3% / +3%")
    print("=" * 80)
    print(f"  قیمت فعلی:           {int(last):,}")
    print(f"  🟢 خرید (-3%):       {int(buy_target):,}")
    print(f"  🔴 فروش (+3%):       {int(sell_target):,}")
    print(f"  ⛔ حد ضرر (-2% از خرید): {int(stop_loss):,}")
    print()
    print(f"  💡 سود خالص (بعد کارمزد ۱.۲۵%): ~{3 - 1.25:.2f}%")
    print(f"  💡 ریسک/ریوارد: 1:{3/2:.2f}")
    print()

    # ارزیابی
    print("=" * 80)
    print(f"  📋 ارزیابی برای استراتژی نوسان")
    print("=" * 80)

    score = 0
    reasons = []

    # RSI
    if rsi and 15 <= rsi <= 55:
        score += 30
        reasons.append(f"✅ RSI مناسب ({rsi})")
    elif rsi and rsi < 15:
        score += 20
        reasons.append(f"⚠️ RSI خیلی پایین ({rsi}) - احتمال ادامه ریزش")
    elif rsi and rsi > 70:
        reasons.append(f"❌ RSI بالا ({rsi}) - اشباع خرید")
    else:
        score += 10
        reasons.append(f"🟡 RSI متوسط ({rsi})")

    # ATR
    if atr_pct >= 3.0:
        score += 30
        reasons.append(f"✅ نوسان کافی (ATR={atr_pct:.1f}%)")
    elif atr_pct >= 2.0:
        score += 20
        reasons.append(f"🟡 نوسان متوسط (ATR={atr_pct:.1f}%)")
    else:
        reasons.append(f"❌ نوسان کم (ATR={atr_pct:.1f}%) - سود ۳٪ سخته")

    # روند
    if "صعودی" in trend:
        score += 20
        reasons.append("✅ روند صعودی")
    elif "خنثی" in trend:
        score += 10
        reasons.append("🟡 روند خنثی")
    else:
        reasons.append("❌ روند نزولی")

    # فاصله از مقاومت
    distance_to_resistance = (resistance_20 - last) / last * 100
    if distance_to_resistance >= 3:
        score += 20
        reasons.append(f"✅ فضا تا مقاومت ({distance_to_resistance:.1f}%)")
    else:
        reasons.append(f"⚠️ نزدیک مقاومت ({distance_to_resistance:.1f}%)")

    for r in reasons:
        print(f"  {r}")

    print()
    print(f"  🎯 امتیاز کل: {score}/100")

    if score >= 70:
        print(f"  ✅ مناسب برای نوسان‌گیری")
    elif score >= 50:
        print(f"  🟡 نسبتاً مناسب - با احتیاط")
    else:
        print(f"  ❌ مناسب نیست")

    return {
        "symbol": symbol,
        "price": last,
        "rsi": rsi,
        "atr_pct": atr_pct,
        "trend": trend,
        "score": score,
    }


def main():
    print()
    print("=" * 80)
    print("  🔍 تحلیل فولاد مبارکه و خگستر")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = []
    for symbol in SYMBOLS:
        r = analyze(symbol)
        if r:
            results.append(r)

    # مقایسه
    if len(results) >= 2:
        print()
        print("=" * 80)
        print("  📊 مقایسه نهایی")
        print("=" * 80)
        print()
        print(f"  {'نماد':<10} | {'قیمت':>10} | {'RSI':>6} | {'ATR%':>6} | {'امتیاز':>7}")
        print("  " + "-" * 55)
        for r in results:
            print(f"  {r['symbol']:<10} | {int(r['price']):>10,} | {str(r['rsi']):>6} | {r['atr_pct']:>6.1f} | {r['score']:>5}/100")

        best = max(results, key=lambda x: x["score"])
        print()
        print(f"  🏆 بهترین: {best['symbol']} با امتیاز {best['score']}/100")
        print()


if __name__ == "__main__":
    main()
