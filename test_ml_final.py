# test_ml_final.py
# تست نهایی ML
# اجرا: python test_ml_final.py

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
    safe_print("  🧪 تست نهایی ML")
    safe_print("=" * 80)
    safe_print("")

    # ۱. import
    from ai.ai_engine import AIEngine
    engine = AIEngine()
    safe_print("  ✅ ai_engine import")
    safe_print(f"  ✅ ML ready: {engine.ml_model.is_ready()}")
    safe_print("")

    # ۲. تست‌های مختلف
    tests = [
        # (symbol, category, ratio, rsi, tech, market, price)
        ("خگستر", "SAFE_BUY", 5.0, 25, 70, 1.5, 10000),
        ("فولاد", "SAFE_BUY", 2.0, 35, 60, 0.5, 5000),
        ("خپارس", "SAFE_BUY", 10.0, 20, 80, 2.0, 3000),
        ("تابان", "SAFE_SELL", 0.3, 75, 30, -1.5, 2000),
        ("احیا", "SAFE_BUY", 1.5, 45, 55, 0.0, 8000),
    ]

    safe_print("  📊 تست سناریوها:")
    safe_print("")

    for i, (sym, cat, ratio, rsi, tech, market, price) in enumerate(tests, 1):
        result = engine.advise(
            symbol=sym,
            category=cat,
            ratio=ratio,
            rsi=rsi,
            technical_score=tech,
            market_change_pct=market,
            last_price=price,
        )
        
        safe_print(f"  {i}. {sym} ({cat})")
        safe_print(f"     ratio={ratio}, rsi={rsi}, tech={tech}, market={market}")
        safe_print(f"     weight_score: {result['weight_score']}")
        safe_print(f"     ml_score: {result['ml_score']}")
        safe_print(f"     final_score: {result['final_score']}")
        safe_print(f"     mode: {result['mode']}")
        safe_print(f"     advice: {result['advice']}")
        safe_print("")

    # ۳. گزارش
    safe_print("  📊 گزارش AI:")
    engine.report()

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
