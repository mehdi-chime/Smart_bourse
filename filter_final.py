# filter_final.py
# فیلتر نهایی — بهترین ترکیب
# اجرا: python filter_final.py

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
    safe_print("  🎯 فیلتر نهایی")
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

    filters = [
        ("RSI < 30", lambda d: d["rsi"] < 30),
        ("RSI < 35", lambda d: d["rsi"] < 35),
        ("RSI < 40", lambda d: d["rsi"] < 40),
        ("RSI < 45", lambda d: d["rsi"] < 45),
        ("RSI < 40 + ratio 0.5-2", lambda d: d["rsi"] < 40 and 0.5 <= d["ratio"] < 2),
        ("RSI < 35 + ratio 0.5-2", lambda d: d["rsi"] < 35 and 0.5 <= d["ratio"] < 2),
        ("RSI < 40 + ratio > 0.5", lambda d: d["rsi"] < 40 and d["ratio"] > 0.5),
        ("RSI < 35 + ratio > 0.5", lambda d: d["rsi"] < 35 and d["ratio"] > 0.5),
        ("RSI < 45 + ratio > 0.5", lambda d: d["rsi"] < 45 and d["ratio"] > 0.5),
    ]

    safe_print(f"  {'فیلتر':<30} | {'تعداد':>6} | {'موفق':>6} | {'Win Rate':>10}")
    safe_print("  " + "-" * 70)

    best = None

    for name, func in filters:
        filtered = [d for d in data if func(d)]
        if not filtered:
            continue

        success = sum(1 for d in filtered if d["success"])
        total = len(filtered)
        wr = success / total * 100

        safe_print(f"  {name:<30} | {total:>6} | {success:>6} | {wr:>9.1f}%")

        if best is None or wr > best[1]:
            best = (name, wr, total, success)

    safe_print("")
    if best:
        safe_print(f"  🏆 بهترین: {best[0]} | {best[1]:.1f}% ({best[3]}/{best[2]})")
    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
