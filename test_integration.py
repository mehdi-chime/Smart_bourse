# test_integration.py
# تست ai_integration
# اجرا: python test_integration.py

import os
import sys
from pathlib import Path

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
    safe_print("  🧪 تست ai_integration")
    safe_print("=" * 80)
    safe_print("")

    # ۱. import
    safe_print("  📦 import...")
    try:
        from ai_integration import get_ai_advice, record_ai_signal, enhance_scanner_results
        safe_print("     ✅ import موفق")
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        return
    safe_print("")

    # ۲. تست get_ai_advice
    safe_print("  📊 تست get_ai_advice...")
    result = get_ai_advice(
        symbol="خگستر",
        category="SAFE_BUY",
        ratio=5.0,
        rsi=25,
        technical_score=70,
        market_change_pct=1.5,
        last_price=10000,
    )
    safe_print(f"     symbol: {result.get('symbol')}")
    safe_print(f"     final_score: {result.get('final_score')}")
    safe_print(f"     advice: {result.get('advice')}")
    safe_print(f"     confidence: {result.get('confidence')}")
    safe_print(f"     mode: {result.get('mode')}")
    safe_print("")

    # ۳. تست record_ai_signal
    safe_print("  📝 تست record_ai_signal...")
    ok = record_ai_signal(
        symbol="تست",
        category="SAFE_BUY",
        ratio=3.0,
        rsi=30,
        technical_score=60,
        last_price=5000,
    )
    safe_print(f"     ✅ {ok}")
    safe_print("")

    # ۴. تست enhance_scanner_results
    safe_print("  🔧 تست enhance_scanner_results...")
    test_results = [
        {"symbol": "فولاد", "ratio": 3.0, "rsi": 35, "score": 70, "last": 5000},
        {"symbol": "خپارس", "ratio": 5.0, "rsi": 25, "score": 80, "last": 3000},
    ]
    enhanced = enhance_scanner_results(test_results)
    
    for r in enhanced:
        safe_print(f"     {r.get('symbol')}:")
        safe_print(f"        ai_score: {r.get('ai_score')}")
        safe_print(f"        ai_advice: {r.get('ai_advice')}")
        safe_print(f"        ai_mode: {r.get('ai_mode')}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
