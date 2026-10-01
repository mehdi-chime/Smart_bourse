# test_ml.py
# تست ML — فاز ۲
# اجرا: python test_ml.py

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
    safe_print("  🧪 تست ML — فاز ۲")
    safe_print("=" * 80)
    safe_print("")

    # ۱. import
    safe_print("  📦 import...")
    try:
        from ai.ml_model import MLModel
        from ai.trainer import AITrainer
        safe_print("     ✅ ml_model")
        safe_print("     ✅ trainer")
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        return
    safe_print("")

    # ۲. چک sklearn
    safe_print("  🔍 چک sklearn...")
    model = MLModel()
    safe_print(f"     Has sklearn: {model.has_sklearn}")
    safe_print(f"     Model ready: {model.is_ready()}")
    safe_print("")

    # ۳. بارگذاری نتایج
    safe_print("  📂 بارگذاری نتایج...")
    trainer = AITrainer()
    outcomes = trainer.load_outcomes()
    safe_print(f"     ✅ {len(outcomes)} نتیجه")
    safe_print("")

    # ۴. آموزش
    if len(outcomes) >= 10:
        safe_print("  🎓 آموزش مدل...")
        result = trainer.train_from_outcomes()
        safe_print(f"     status: {result.get('status')}")
        safe_print(f"     samples: {result.get('samples', 0)}")
        safe_print(f"     success: {result.get('success_count', 0)}")
        safe_print(f"     fail: {result.get('fail_count', 0)}")
    else:
        safe_print(f"  ⚠️ داده کافی نیست ({len(outcomes)} از 10)")
    safe_print("")

    # ۵. چک مدل
    safe_print("  📊 چک مدل...")
    model2 = MLModel()
    safe_print(f"     Model ready: {model2.is_ready()}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
