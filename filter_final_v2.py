# filter_final_v2.py
# فیلتر نهایی — نسخه ۲ (دقیق‌تر)
# اجرا: python filter_final_v2.py

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
    safe_print("  🎯 فیلتر نهایی — نسخه ۲")
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
        ("RSI < 20", lambda d: d["rsi"] < 20),
        ("RSI < 25", lambda d: d["rsi"] < 25),
        ("RSI < 28", lambda d: d["rsi"] < 28),
        ("RSI < 30", lambda d: d["rsi"] < 30),
        ("RSI < 32", lambda d: d["rsi"] < 32),
        ("RSI < 35", lambda d: d["rsi"] < 35),
        ("RSI 20-30", lambda d: 20 <= d["rsi"] < 30),
        ("RSI 25-35", lambda d: 25 <= d["rsi"] < 35),
        ("RSI 30-40", lambda d: 30 <= d["rsi"] < 40),
        ("RSI < 30 + ratio < 1", lambda d: d["rsi"] < 30 and d["ratio"] < 1),
        ("RSI < 30 + ratio 1-2", lambda d: d["rsi"] < 30 and 1 <= d["ratio"] < 2),
        ("RSI < 30 + ratio > 2", lambda d: d["rsi"] < 30 and d["ratio"] >= 2),
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
