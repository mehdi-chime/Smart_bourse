# filter_golden.py
# فیلتر طلایی — RSI 25-28
# اجرا: python filter_golden.py

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


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🏆 فیلتر طلایی")
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
            "ratio": sig.get("ratio", 1),
            "rsi": sig.get("rsi", 50) or 50,
            "success": success,
        })

    safe_print(f"  📊 کل: {len(data)} سیگنال")
    safe_print("")

    # بازه‌های دقیق
    filters = [
        ("RSI < 18", lambda d: d["rsi"] < 18),
        ("RSI 18-20", lambda d: 18 <= d["rsi"] < 20),
        ("RSI 20-22", lambda d: 20 <= d["rsi"] < 22),
        ("RSI 22-24", lambda d: 22 <= d["rsi"] < 24),
        ("RSI 24-26", lambda d: 24 <= d["rsi"] < 26),
        ("RSI 26-28", lambda d: 26 <= d["rsi"] < 28),
        ("RSI 28-30", lambda d: 28 <= d["rsi"] < 30),
        ("RSI 30-32", lambda d: 30 <= d["rsi"] < 32),
        ("RSI 25-28", lambda d: 25 <= d["rsi"] < 28),
        ("RSI 25-30", lambda d: 25 <= d["rsi"] < 30),
    ]

    safe_print(f"  {'بازه':<20} | {'تعداد':>6} | {'موفق':>6} | {'Win Rate':>10}")
    safe_print("  " + "-" * 65)

    best = None

    for name, func in filters:
        filtered = [d for d in data if func(d)]
        if not filtered:
            continue

        success = sum(1 for d in filtered if d["success"])
        total = len(filtered)
        wr = success / total * 100

        emoji = "🏆" if wr > 50 else ("🟢" if wr > 40 else "🔴")
        safe_print(f"  {name:<20} | {total:>6} | {success:>6} | {emoji} {wr:>8.1f}%")

        if best is None or wr > best[1]:
            best = (name, wr, total, success)

    safe_print("")
    if best:
        safe_print(f"  🏆 بهترین: {best[0]} | {best[1]:.1f}% ({best[3]}/{best[2]})")
    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
