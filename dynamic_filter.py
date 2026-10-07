# dynamic_filter.py
# فیلتر داینامیک — بسته به بازار
# اجرا: python dynamic_filter.py

import os
import sys
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
    safe_print("  🎯 فیلتر داینامیک")
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

    # ۱. محاسبه RSI همه
    safe_print("  🔍 محاسبه RSI...")

    rsi_values = []

    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            continue

        hist = get_history_safe(symbol)
        if hist is None:
            continue

        closes = hist["Close"].tolist()
        rsi = calc_rsi(closes, 14)
        if rsi is not None:
            rsi_values.append(rsi)

    if not rsi_values:
        safe_print("  ❌ هیچ RSI محاسبه نشد!")
        return

    # ۲. تحلیل بازار
    avg_rsi = sum(rsi_values) / len(rsi_values)

    safe_print(f"     تعداد: {len(rsi_values)}")
    safe_print(f"     میانگین RSI: {avg_rsi:.1f}")
    safe_print("")

    # ۳. تنظیم بازه
    if avg_rsi > 60:
        MIN_RSI = 28
        MAX_RSI = 40
        market_state = "داغ"
    elif avg_rsi < 40:
        MIN_RSI = 22
        MAX_RSI = 30
        market_state = "سرد"
    else:
        MIN_RSI = 22
        MAX_RSI = 28
        market_state = "معمولی"

    safe_print(f"  📊 وضعیت بازار: {market_state}")
    safe_print(f"  🎯 بازه: {MIN_RSI}-{MAX_RSI}")
    safe_print("")

    # ۴. فیلتر
    safe_print("  🔍 فیلتر...")

    candidates = []

    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            continue

        last = float(row.get("Last") or row.get("Close") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0:
            continue

        pe = None
        if eps > 0:
            pe = round(last / eps, 2)
            if pe > 15 or pe < 0:
                continue

        hist = get_history_safe(symbol)
        if hist is None:
            continue

        closes = hist["Close"].tolist()
        rsi = calc_rsi(closes, 14)
        if rsi is None:
            continue

        # فیلتر داینامیک
        if not (MIN_RSI <= rsi < MAX_RSI):
            continue

        # امتیاز
        score = 0

        # RSI: ۵۰
        mid = (MIN_RSI + MAX_RSI) / 2
        if abs(rsi - mid) < 2:
            score += 50
        elif abs(rsi - mid) < 4:
            score += 30
        else:
            score += 10

        # P/E: ۳۰
        if pe:
            if pe < 5:
                score += 30
            elif pe < 8:
                score += 20
            elif pe < 12:
                score += 10

        # تغییر: ۲۰
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

    safe_print(f"     ✅ {len(candidates)} سهم")
    safe_print("")

    if not candidates:
        safe_print("  ❌ هیچ سهمی پیدا نشد!")
        return

    # نمایش
    candidates.sort(key=lambda x: -x["score"])

    safe_print("=" * 80)
    safe_print(f"  🏆 بهترین سهم‌ها (RSI {MIN_RSI}-{MAX_RSI})")
    safe_print("=" * 80)
    safe_print("")

    for i, c in enumerate(candidates[:20], 1):
        safe_print(
            f"  {i:<3} | "
            f"{c['symbol'][:15]:<15} | "
            f"{int(c['last']):>10,} | "
            f"{c['change']:>+6.2f}% | "
            f"P/E: {c['pe'] if c['pe'] else '?':>5} | "
            f"RSI: {c['rsi']:>5} | "
            f"{c['score']:>4}/100"
        )

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
