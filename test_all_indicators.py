# test_all_indicators.py
# تست همه اندیکاتورها
# اجرا: python test_all_indicators.py

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def calc_macd(prices, fast=12, slow=26, signal=9):
    """محاسبه MACD"""
    if len(prices) < slow + signal:
        return None

    p = np.array(prices, dtype=float)
    ema_fast = np.mean(p[-fast:])
    ema_slow = np.mean(p[-slow:])

    macd_line = ema_fast - ema_slow

    # سیگنال (ساده)
    signal_line = macd_line * 0.9

    histogram = macd_line - signal_line

    return {
        "macd": round(macd_line, 2),
        "signal": round(signal_line, 2),
        "histogram": round(histogram, 2),
    }


def calc_bollinger(prices, period=20, std_dev=2):
    """محاسبه Bollinger"""
    if len(prices) < period:
        return None

    p = np.array(prices[-period:], dtype=float)
    sma = np.mean(p)
    std = np.std(p)

    upper = sma + std_dev * std
    lower = sma - std_dev * std

    current = prices[-1]

    # موقعیت
    if current >= upper:
        position = "بالای باند"
    elif current <= lower:
        position = "زیر باند"
    else:
        position = "داخل باند"

    return {
        "upper": round(upper, 2),
        "middle": round(sma, 2),
        "lower": round(lower, 2),
        "current": round(current, 2),
        "position": position,
    }


def calc_adx(highs, lows, closes, period=14):
    """محاسبه ADX (ساده)"""
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

    atr = np.mean(trs[-period:])

    # جهت (ساده)
    up = 0
    down = 0
    for i in range(-period, 0):
        if closes[i] > closes[i-1]:
            up += 1
        else:
            down += 1

    if up + down == 0:
        return None

    di_plus = up / (up + down) * 100
    di_minus = down / (up + down) * 100

    dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100 if (di_plus + di_minus) > 0 else 0

    return {
        "adx": round(dx, 1),
        "di_plus": round(di_plus, 1),
        "di_minus": round(di_minus, 1),
    }


def calc_supertrend(highs, lows, closes, period=10, multiplier=3):
    """محاسبه SuperTrend (ساده)"""
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

    atr = np.mean(trs[-period:])
    hl2 = (highs[-1] + lows[-1]) / 2

    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    current = closes[-1]

    if current > upper_band:
        trend = "صعودی"
    elif current < lower_band:
        trend = "نزولی"
    else:
        trend = "خنثی"

    return {
        "trend": trend,
        "upper": round(upper_band, 2),
        "lower": round(lower_band, 2),
    }


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 تست همه اندیکاتورها")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # بارگذاری
    from ai.memory import AIMemory
    memory = AIMemory()

    signals = memory.load_signals()
    outcomes = memory.load_outcomes()

    safe_print(f"  📊 سیگنال‌ها: {len(signals)}")
    safe_print(f"  📊 نتایج: {len(outcomes)}")
    safe_print("")

    # نقشه
    signal_map = {}
    for s in signals:
        key = (s.get("date"), s.get("symbol"))
        signal_map[key] = s

    # داده
    data = []
    for o in outcomes:
        key = (o.get("date"), o.get("symbol"))
        sig = signal_map.get(key)

        if not sig:
            continue

        success = o.get("success")
        if success is None:
            continue

        data.append({
            "symbol": sig.get("symbol"),
            "date": sig.get("date"),
            "rsi": sig.get("rsi", 50) or 50,
            "ratio": sig.get("ratio", 1),
            "success": success,
        })

    safe_print(f"  📊 داده: {len(data)}")
    safe_print("")

    # برای هر سهم، اندیکاتورها رو محاسبه کن
    import algotik_tse as att

    safe_print("  🔍 محاسبه اندیکاتورها...")

    # نمونه: ۱۰ سهم
    unique_symbols = list(set(d["symbol"] for d in data))[:10]

    for symbol in unique_symbols:
        safe_print(f"     {symbol}...")

        try:
            hist = att.get_history(symbol)
            if hist is None or hist.empty:
                continue

            closes = hist["Close"].tolist()
            highs = hist["High"].tolist() if "High" in hist.columns else closes
            lows = hist["Low"].tolist() if "Low" in hist.columns else closes

            # محاسبه
            macd = calc_macd(closes)
            bb = calc_bollinger(closes)
            adx = calc_adx(highs, lows, closes)
            st = calc_supertrend(highs, lows, closes)

            safe_print(f"        MACD: {macd}")
            safe_print(f"        Bollinger: {bb.get('position') if bb else '?'}")
            safe_print(f"        ADX: {adx.get('adx') if adx else '?'}")
            safe_print(f"        SuperTrend: {st.get('trend') if st else '?'}")

        except Exception as e:
            safe_print(f"        ❌ {e}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
