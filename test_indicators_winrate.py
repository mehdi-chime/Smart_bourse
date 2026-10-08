# test_indicators_winrate.py
# تست Win Rate با اندیکاتورها
# اجرا: python test_indicators_winrate.py

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

import algotik_tse as att


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def calc_macd(prices, fast=12, slow=26):
    if len(prices) < slow:
        return None
    p = np.array(prices, dtype=float)
    ema_fast = np.mean(p[-fast:])
    ema_slow = np.mean(p[-slow:])
    return float(ema_fast - ema_slow)


def calc_bollinger_position(prices, period=20, std_dev=2):
    if len(prices) < period:
        return None
    p = np.array(prices[-period:], dtype=float)
    sma = np.mean(p)
    std = np.std(p)
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    current = prices[-1]

    if current >= upper:
        return "بالای باند"
    elif current <= lower:
        return "زیر باند"
    return "داخل باند"


def calc_adx(highs, lows, closes, period=14):
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

    up = 0
    down = 0
    for i in range(-period, 0):
        if closes[i] > closes[i-1]:
            up += 1
        else:
            down += 1

    if up + down == 0:
        return 0

    di_plus = up / (up + down) * 100
    di_minus = down / (up + down) * 100

    dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100 if (di_plus + di_minus) > 0 else 0

    return round(dx, 1)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🎯 تست Win Rate با اندیکاتورها")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    from ai.memory import AIMemory
    memory = AIMemory()

    signals = memory.load_signals()
    outcomes = memory.load_outcomes()

    signal_map = {}
    for s in signals:
        key = (s.get("date"), s.get("symbol"))
        signal_map[key] = s

    # جمع‌آوری داده با اندیکاتورها
    safe_print("  📊 جمع‌آوری داده...")

    data = []
    processed = 0

    for o in outcomes:
        key = (o.get("date"), o.get("symbol"))
        sig = signal_map.get(key)

        if not sig:
            continue

        success = o.get("success")
        if success is None:
            continue

        symbol = sig.get("symbol")
        rsi = sig.get("rsi", 50) or 50

        # تاریخچه
        try:
            hist = att.get_history(symbol)
            if hist is None or hist.empty:
                continue

            closes = hist["Close"].tolist()
            highs = hist["High"].tolist() if "High" in hist.columns else closes
            lows = hist["Low"].tolist() if "Low" in hist.columns else closes

            macd = calc_macd(closes)
            bb = calc_bollinger_position(closes)
            adx = calc_adx(highs, lows, closes)

            if macd is None or bb is None or adx is None:
                continue

            data.append({
                "symbol": symbol,
                "rsi": rsi,
                "macd": macd,
                "bb": bb,
                "adx": adx,
                "success": success,
            })

            processed += 1
            if processed % 50 == 0:
                safe_print(f"     {processed}...")

        except:
            continue

    safe_print(f"  ✅ {len(data)} داده")
    safe_print("")

    if not data:
        safe_print("  ❌ داده کافی نیست!")
        return

    # تست فیلترها
    filters = [
        ("RSI 22-28", lambda d: 22 <= d["rsi"] < 28),
        ("RSI 22-28 + MACD > 0", lambda d: 22 <= d["rsi"] < 28 and d["macd"] > 0),
        ("RSI 22-28 + MACD < 0", lambda d: 22 <= d["rsi"] < 28 and d["macd"] < 0),
        ("RSI 22-28 + BB زیر باند", lambda d: 22 <= d["rsi"] < 28 and d["bb"] == "زیر باند"),
        ("RSI 22-28 + BB داخل باند", lambda d: 22 <= d["rsi"] < 28 and d["bb"] == "داخل باند"),
        ("RSI 22-28 + ADX > 25", lambda d: 22 <= d["rsi"] < 28 and d["adx"] > 25),
        ("RSI 22-28 + ADX > 40", lambda d: 22 <= d["rsi"] < 28 and d["adx"] > 40),
        ("RSI 22-28 + MACD > 0 + ADX > 25", lambda d: 22 <= d["rsi"] < 28 and d["macd"] > 0 and d["adx"] > 25),
        ("RSI 22-28 + BB زیر باند + ADX > 25", lambda d: 22 <= d["rsi"] < 28 and d["bb"] == "زیر باند" and d["adx"] > 25),
    ]

    safe_print(f"  {'فیلتر':<40} | {'تعداد':>6} | {'موفق':>6} | {'Win Rate':>10}")
    safe_print("  " + "-" * 80)

    best = None

    for name, func in filters:
        filtered = [d for d in data if func(d)]
        if not filtered:
            continue

        success = sum(1 for d in filtered if d["success"])
        total = len(filtered)
        wr = success / total * 100

        emoji = "🏆" if wr > 60 else ("🟢" if wr > 50 else "🟡")
        safe_print(f"  {name:<40} | {total:>6} | {success:>6} | {emoji} {wr:>8.1f}%")

        if best is None or wr > best[1]:
            best = (name, wr, total, success)

    safe_print("")
    if best:
        safe_print(f"  🏆 بهترین: {best[0]} | {best[1]:.1f}% ({best[3]}/{best[2]})")
    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
