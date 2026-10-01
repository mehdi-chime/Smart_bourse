# fix_ml_features.py
# اصلاح ai_engine.py برای ۶ ویژگی ML
# اجرا: python fix_ml_features.py

import os
import sys
import re
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
AI_ENGINE = PROJECT_ROOT / "ai" / "ai_engine.py"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔧 اصلاح ai_engine.py (۶ ویژگی ML)")
    safe_print("=" * 80)
    safe_print("")

    if not AI_ENGINE.exists():
        safe_print("  ❌ ai_engine.py پیدا نشد!")
        return

    content = AI_ENGINE.read_text(encoding="utf-8")

    # پیدا کردن بخش ML prediction
    old_pattern = r'''        # ML prediction
        ml_score = None
        if self\.ml_model and self\.ml_model\.is_ready\(\) and last_price:
            try:
                X = \[\[
                    last_price,
                    0,
                    0,
                    0,
                \]\]
                proba = self\.ml_model\.predict_proba\(X\)
                if proba is not None and len\(proba\) > 0:
                    ml_score = round\(proba\[0\]\[1\] \* 100, 1\)
            except Exception:
                pass'''

    new_code = '''        # ML prediction
        ml_score = None
        if self.ml_model and self.ml_model.is_ready() and last_price:
            try:
                X = [[
                    ratio,
                    rsi if rsi is not None else 50,
                    technical_score if technical_score is not None else 50,
                    weight_score,
                    last_price,
                    market_change_pct if market_change_pct is not None else 0,
                ]]
                proba = self.ml_model.predict_proba(X)
                if proba is not None and len(proba) > 0:
                    ml_score = round(proba[0][1] * 100, 1)
            except Exception as e:
                print(f"ML error: {e}")'''

    if "weight_score" in content and "ML prediction" in content:
        safe_print("  ℹ️ شاید از قبل اصلاح شده")
    
    content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
    
    AI_ENGINE.write_text(content, encoding="utf-8")
    safe_print("  ✅ ai_engine.py اصلاح شد")
    safe_print("")

    # تست
    safe_print("  🧪 تست...")
    try:
        import importlib
        if "ai.ai_engine" in sys.modules:
            importlib.reload(sys.modules["ai.ai_engine"])
        
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        
        result = engine.advise(
            symbol="خگستر",
            category="SAFE_BUY",
            ratio=5.0,
            rsi=25,
            technical_score=70,
            market_change_pct=1.5,
            last_price=10000,
        )
        
        safe_print(f"     weight_score: {result['weight_score']}")
        safe_print(f"     ml_score: {result['ml_score']}")
        safe_print(f"     final_score: {result['final_score']}")
        safe_print(f"     mode: {result['mode']}")
        safe_print(f"     advice: {result['advice']}")
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
