# filter_ratio.py
# تست فیلتر ratio < 2
# اجرا: python filter_ratio.py

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
    safe_print("  🎯 تست فیلتر ratio < 2")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    from ai.memory import AIMemory
    memory = AIMemory()

    signals = memory.load_signals()
    outcomes = memory.load_outcomes()

    # نقشه
    signal_map = {}
    for s in signals:
        key = (s.get("date"), s.get("symbol"))
        signal_map[key] = s

    # دسته‌بندی
    low = []
    high = []

    for o in outcomes:
        key = (o.get("date"), o.get("symbol"))
        sig = signal_map.get(key)

        if not sig:
            continue

        success = o.get("success")
        if success is None:
            continue

        ratio = sig.get("ratio", 1)

        if ratio < 2:
            low.append(success)
        else:
            high.append(success)

    # نمایش
    safe_print(f"  📊 ratio < 2: {len(low)} سیگنال")
    if low:
        wr = sum(low) / len(low) * 100
        safe_print(f"     ✅ موفق: {sum(low)}")
        safe_print(f"     ❌ ناموفق: {len(low) - sum(low)}")
        safe_print(f"     🎯 Win Rate: {wr:.1f}%")
    safe_print("")

    safe_print(f"  📊 ratio >= 2: {len(high)} سیگنال")
    if high:
        wr = sum(high) / len(high) * 100
        safe_print(f"     ✅ موفق: {sum(high)}")
        safe_print(f"     ❌ ناموفق: {len(high) - sum(high)}")
        safe_print(f"     🎯 Win Rate: {wr:.1f}%")
    safe_print("")

    # کل
    total = low + high
    if total:
        wr = sum(total) / len(total) * 100
        safe_print(f"  📊 کل: {len(total)} سیگنال | Win Rate: {wr:.1f}%")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
