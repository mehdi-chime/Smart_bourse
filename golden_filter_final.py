# golden_filter_final.py
# فیلتر طلایی نهایی — برای اسکنر
# اجرا: python golden_filter_final.py

import os
import sys
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
import numpy as np


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
            .replace(" ", "")
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


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🏆 فیلتر طلایی — RSI 22-28")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # دریافت
    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    # فیلتر
    safe_print("  🔍 فیلتر RSI 22-28...")
    safe_print("")

    candidates = []

    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if not symbol:
            continue

        if symbol.endswith("3") or symbol.endswith("ح"):
            continue

        last = float(row.get("Last") or row.get("Close") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0:
            continue

        # P/E
        pe = None
        if eps > 0:
            pe = round(last / eps, 2)
            if pe > 15 or pe < 0:
                continue

        # RSI
        hist = get_history_safe(symbol)
        if hist is None:
            continue

        closes = hist["Close"].tolist()
        rsi = calc_rsi(closes, 14)

        if rsi is None:
            continue

        # فیلتر طلایی
        if not (22 <= rsi < 28):
            continue

        # امتیاز
        score = 0

        # RSI (60)
        if 24 <= rsi < 26:
            score += 60
        elif 22 <= rsi < 24:
            score += 45
        elif 26 <= rsi < 28:
            score += 30

        # P/E (20)
        if pe:
            if pe < 5:
                score += 20
            elif pe < 8:
                score += 15
            elif pe < 12:
                score += 10

        # تغییر (20)
        if change < -3:
            score += 20
        elif change < -1:
            score += 10

        candidates.append({
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "change": change,
            "pe": pe,
            "rsi": rsi,
            "score": score,
        })

    safe_print(f"  ✅ {len(candidates)} سهم")
    safe_print("")

    if not candidates:
        safe_print("  ❌ هیچ سهمی پیدا نشد!")
        return

    # مرتب‌سازی
    candidates.sort(key=lambda x: -x["score"])

    safe_print("=" * 80)
    safe_print("  🏆 نتایج")
    safe_print("=" * 80)
    safe_print("")
    safe_print(f"  {'#':<3} | {'نماد':<15} | {'قیمت':>10} | {'تغییر':>7} | {'P/E':>5} | {'RSI':>5} | {'امتیاز':>6}")
    safe_print("  " + "-" * 80)

    for i, c in enumerate(candidates[:20], 1):
        safe_print(
            f"  {i:<3} | "
            f"{c['symbol'][:15]:<15} | "
            f"{int(c['last']):>10,} | "
            f"{c['change']:>+6.2f}% | "
            f"{c['pe'] if c['pe'] else '?':>5} | "
            f"{c['rsi']:>5} | "
            f"{c['score']:>4}/100"
        )

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
