# improve_ai_v4.py
# آموزش مجدد ML — نسخه ۴
# اجرا: python improve_ai_v4.py

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
    safe_print("  🎓 آموزش مجدد ML — نسخه ۴")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بارگذاری
    safe_print("  📂 بارگذاری داده...")

    from ai.memory import AIMemory
    from ai.ml_model import MLModel

    memory = AIMemory()
    signals = memory.load_signals()
    outcomes = memory.load_outcomes()

    safe_print(f"     سیگنال‌ها: {len(signals)}")
    safe_print(f"     نتایج: {len(outcomes)}")
    safe_print("")

    # ۲. نقشه
    signal_map = {}
    for s in signals:
        key = (s.get("date"), s.get("symbol"))
        signal_map[key] = s

    # ۳. ویژگی‌ها
    safe_print("  🔧 ساخت dataset...")

    X = []
    y = []

    for o in outcomes:
        key = (o.get("date"), o.get("symbol"))
        sig = signal_map.get(key)

        success = o.get("success")
        if success is None:
            continue

        # ویژگی‌ها
        features = [
            sig.get("ratio", 1) if sig else 1,
            sig.get("rsi", 50) if sig and sig.get("rsi") else 50,
            sig.get("technical_score", 50) if sig and sig.get("technical_score") else 50,
            sig.get("final_score", 50) if sig and sig.get("final_score") else 50,
            sig.get("last_price", 0) if sig else 0,
            (sig.get("context") or {}).get("market_change_pct", 0) if sig else 0,
        ]

        X.append(features)
        y.append(1 if success else 0)

    safe_print(f"     نمونه‌ها: {len(X)}")
    safe_print(f"     ✅ موفق: {sum(y)}")
    safe_print(f"     ❌ ناموفق: {len(y) - sum(y)}")
    safe_print("")

    if len(X) < 10:
        safe_print("  ⚠️ نمونه کافی نیست!")
        return

    # ۴. آموزش
    safe_print("  🎓 آموزش مدل...")

    model = MLModel()
    success = model.train(X, y)

    if success:
        safe_print("     ✅ آموزش موفق")
        safe_print(f"     📊 مدل ذخیره شد: {model.model_file}")
    else:
        safe_print("     ❌ آموزش خطا")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
