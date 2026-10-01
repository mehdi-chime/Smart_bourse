
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np


# ID های مستقیم برای سهم‌های مشکل‌دار
SYMBOL_IDS = {
    "تابان": "30714151942396396",
    "احیا": "20092044608974663",
}

# aliases برای بقیه
SYMBOL_ALIASES = {
    "پکویر": ["پكوير", "پکویر"],
    "سمهریز": ["سهرمز", "سمهریز"],
    "پیزد": ["پیزد"],
    "خپارس": ["خپارس"],
    "خگستر": ["خگستر"],
    "فولاد": ["فولاد"],
}


def get_history_safe(name):
    """اول با ID، بعد با aliases"""
    # 1. با ID مستقیم
    if name in SYMBOL_IDS:
        try:
            df = att.get_history(SYMBOL_IDS[name])
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 10:
                    return df
        except Exception as e:
            pass

    # 2. با aliases
    aliases = SYMBOL_ALIASES.get(name, [name])
    for alias in aliases:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 10:
                    return df
        except Exception:
            continue

    return None


def fibonacci_levels(high, low):
    diff = high - low
    if diff <= 0:
        return {}
    return {
        "0.0": high,
        "23.6": high - diff * 0.236,
        "38.2": high - diff * 0.382,
        "50.0": high - diff * 0.500,
        "61.8": high - diff * 0.618,
        "78.6": high - diff * 0.786,
        "100.0": low,
    }


def find_sr_filtered(closes, last_price):
    prices = list(closes)[-120:]
    recent_30 = prices[-30:]
    recent_60 = prices[-60:]

    low_30 = min(recent_30)
    high_30 = max(recent_30)
    low_60 = min(recent_60)
    high_60 = max(recent_60)

    supports = []
    resistances = []

    for level in [low_30, low_60]:
        if level < last_price * 0.97:
            dist = (last_price - level) / last_price * 100
            if 3 < dist < 25:
                supports.append(level)

    for level in [high_30, high_60]:
        if level > last_price * 1.03:
            dist = (level - last_price) / last_price * 100
            if 3 < dist < 25:
                resistances.append(level)

    return sorted(set(supports), reverse=True), sorted(set(resistances))


def atr(highs, lows, closes, period=14):
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


def bollinger(prices, period=20, std_mult=2):
    if len(prices) < period:
        return None
    recent = prices[-period:]
    ma = float(np.mean(recent))
    std = float(np.std(recent))
    return {
        "upper": ma + std_mult * std,
        "middle": ma,
        "lower": ma - std_mult * std,
    }


def get_rsi(prices, period=14):
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
    return 100 - (100 / (1 + rs))


def rsi_status(rsi):
    if rsi is None:
        return "?"
    if rsi >= 99:
        return "قفل صف خرید"
    if rsi >= 80:
        return "اشباع شدید"
    if rsi >= 70:
        return "اشباع خرید"
    if rsi <= 20:
        return "اشباع فروش شدید"
    if rsi <= 30:
        return "اشباع فروش"
    return "نرمال"


def analyze_symbol(name):
    df = get_history_safe(name)
    if df is None or df.empty or "Close" not in df.columns:
        return None

    closes = df["Close"].tolist()
    if len(closes) < 10:
        return None

    closes = closes[-250:]
    highs = df["High"].tolist()[-250:] if "High" in df.columns else closes
    lows = df["Low"].tolist()[-250:] if "Low" in df.columns else closes

    last = closes[-1]

    period = min(60, len(closes))
    recent_closes = closes[-period:]
    high = max(recent_closes)
    low = min(recent_closes)

    fib = fibonacci_levels(high, low)
    supports, resistances = find_sr_filtered(closes, last)
    atr_val = atr(highs[-min(30, len(highs)):], lows[-min(30, len(lows)):], closes[-min(30, len(closes)):], 14)
    bb = bollinger(closes, 20, 2)
    rsi = get_rsi(closes, 14)

    nearest_support = supports[0] if supports else None
    nearest_resistance = resistances[0] if resistances else None

    fib_support = None
    fib_resistance = None
    for fname, level in fib.items():
        dist = abs(level - last) / last * 100
        if dist > 20:
            continue
        if level < last and (fib_support is None or level > fib_support[1]):
            fib_support = (fname, level)
        if level > last and (fib_resistance is None or level < fib_resistance[1]):
            fib_resistance = (fname, level)

    stop_loss = last - 2 * atr_val if atr_val else None

    return {
        "symbol": name,
        "price": last,
        "high_60d": high,
        "low_60d": low,
        "fib_support": fib_support,
        "fib_resistance": fib_resistance,
        "nearest_support": nearest_support,
        "nearest_resistance": nearest_resistance,
        "atr": atr_val,
        "atr_pct": (atr_val / last * 100) if atr_val and last > 0 else None,
        "stop_loss_atr": stop_loss,
        "bollinger": bb,
        "rsi": rsi,
    }


def format_report(name, data, buy_price=None):
    if not data:
        return None

    price = data["price"]
    lines = []
    lines.append("--- " + name + " ---")

    change = 0
    if buy_price:
        change = (price - buy_price) / buy_price * 100
        lines.append("قیمت: " + "{:,}".format(int(price)) + "  " + "{:+.2f}%".format(change))
        lines.append("خرید: " + "{:,}".format(int(buy_price)))
    else:
        lines.append("قیمت: " + "{:,}".format(int(price)))

    rsi = data.get("rsi")
    if rsi is not None:
        lines.append("RSI: " + str(round(rsi, 1)) + "  " + rsi_status(rsi))

    fs = data.get("fib_support")
    fr = data.get("fib_resistance")
    if fs:
        lines.append("حمایت Fib: " + "{:,}".format(int(fs[1])) + " (" + fs[0] + "%)")
    if fr:
        lines.append("مقاومت Fib: " + "{:,}".format(int(fr[1])) + " (" + fr[0] + "%)")

    ns = data.get("nearest_support")
    nr = data.get("nearest_resistance")
    if ns:
        lines.append("حمایت: " + "{:,}".format(int(ns)))
    if nr:
        lines.append("مقاومت: " + "{:,}".format(int(nr)))

    atr_v = data.get("atr")
    atr_p = data.get("atr_pct")
    stop = data.get("stop_loss_atr")
    if atr_v:
        lines.append("")
        lines.append("ATR: " + "{:.0f}".format(atr_v) + " (" + "{:.2f}%".format(atr_p) + ")")
        lines.append("حد ضرر: " + "{:,}".format(int(stop)))

    bb = data.get("bollinger")
    if bb:
        if price < bb["lower"]:
            lines.append("زیر Bollinger - فرصت")
        elif price > bb["upper"]:
            lines.append("بالای Bollinger - خطر")

    lines.append("")
    lines.append("زمان: " + datetime.now().strftime("%H:%M"))
    return "\n".join(lines)


if __name__ == "__main__":
    print()
    print("=" * 75)
    print("  Smart Indicators Analyzer v4 (Final)")
    print("=" * 75)
    print()

    HOLDINGS = [
        {"name": "تابان",   "buy_price": None},
        {"name": "پکویر",   "buy_price": None},
        {"name": "سمهریز",  "buy_price": None},
        {"name": "احیا",    "buy_price": None},
        {"name": "پیزد",    "buy_price": None},
        {"name": "خپارس",   "buy_price": None},
        {"name": "خگستر",   "buy_price": 4327},
        {"name": "فولاد",   "buy_price": 3394},
    ]

    success = 0
    failed = []

    for h in HOLDINGS:
        symbol = h["name"]
        print("Analyzing " + symbol + " ...")
        data = analyze_symbol(symbol)
        if data:
            report = format_report(symbol, data, h["buy_price"])
            print()
            print(report)
            print()
            success += 1
        else:
            print("   no data")
            failed.append(symbol)
        print()

    print("=" * 75)
    print("  Done: " + str(success) + "/" + str(len(HOLDINGS)) + " symbols")
    if failed:
        print("  Failed: " + ", ".join(failed))
    print("=" * 75)
