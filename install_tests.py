# install_tests.py
# فاز ۵: تست خودکار با pytest
# اجرا: python install_tests.py

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
TESTS_DIR = PROJECT_ROOT / "tests"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


# ═══════════════════════════════════════════════════════════
# test_ai.py
# ═══════════════════════════════════════════════════════════

TEST_AI = '''"""
Tests for AI modules
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_import_memory():
    from ai.memory import AIMemory
    assert AIMemory is not None


def test_import_learner():
    from ai.learner import AILearner
    assert AILearner is not None


def test_import_ai_engine():
    from ai.ai_engine import AIEngine
    assert AIEngine is not None


def test_learner_weights():
    from ai.learner import AILearner
    learner = AILearner()
    assert "money_flow" in learner.weights
    assert "technical" in learner.weights
    assert "context" in learner.weights


def test_learner_adjust():
    from ai.learner import AILearner
    learner = AILearner()
    
    outcomes = [
        {"category": "SAFE_BUY", "success": True} for _ in range(8)
    ] + [
        {"category": "SAFE_BUY", "success": False} for _ in range(2)
    ]
    
    new_weights = learner.adjust_weights(outcomes)
    assert sum(new_weights.values()) > 0.99
    assert sum(new_weights.values()) < 1.01


def test_ai_engine_advise():
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
    
    assert "final_score" in result
    assert "advice" in result
    assert "confidence" in result
    assert result["final_score"] >= 0


def test_memory_save_load():
    from ai.memory import AIMemory
    memory = AIMemory()
    
    stats = memory.stats()
    assert "total_signals" in stats
    assert "total_outcomes" in stats
    assert "pending" in stats


def test_ml_model_exists():
    from ai.ml_model import MLModel
    model = MLModel()
    assert model.has_sklearn
'''


# ═══════════════════════════════════════════════════════════
# test_scanner.py
# ═══════════════════════════════════════════════════════════

TEST_SCANNER = '''"""
Tests for scanner modules
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_import_indicators():
    from indicators import rsi
    assert rsi is not None


def test_import_strategy():
    from strategy import signal_engine
    assert signal_engine is not None


def test_import_market():
    from market import api
    assert api is not None


def test_rsi_calculation():
    from indicators.rsi import RSI
    rsi = RSI()
    assert rsi is not None
'''


# ═══════════════════════════════════════════════════════════
# conftest.py
# ═══════════════════════════════════════════════════════════

CONFTEST = '''"""
Pytest configuration
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
'''


# ═══════════════════════════════════════════════════════════
# pytest.ini
# ═══════════════════════════════════════════════════════════

PYTEST_INI = '''[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
'''


def install_pytest():
    """نصب pytest"""
    import subprocess
    safe_print("  📦 نصب pytest...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    
    if result.returncode == 0:
        safe_print("     ✅ pytest نصب شد")
        return True
    else:
        safe_print("     ❌ خطا")
        return False


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🧪 فاز ۵: تست خودکار")
    safe_print("=" * 80)
    safe_print("")

    # ۱. نصب pytest
    install_pytest()
    safe_print("")

    # ۲. ساخت فایل‌ها
    safe_print("  📄 ساخت فایل‌های تست...")
    
    size = write_file(TESTS_DIR / "test_ai.py", TEST_AI)
    safe_print(f"     ✅ tests/test_ai.py ({size:,} b)")
    
    size = write_file(TESTS_DIR / "test_scanner.py", TEST_SCANNER)
    safe_print(f"     ✅ tests/test_scanner.py ({size:,} b)")
    
    size = write_file(TESTS_DIR / "conftest.py", CONFTEST)
    safe_print(f"     ✅ tests/conftest.py ({size:,} b)")
    
    size = write_file(PROJECT_ROOT / "pytest.ini", PYTEST_INI)
    safe_print(f"     ✅ pytest.ini ({size:,} b)")
    safe_print("")

    # ۳. اجرای تست
    safe_print("  🧪 اجرای تست...")
    import subprocess
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
        errors="ignore",
    )
    
    # نمایش خلاصه
    lines = result.stdout.split("\n")
    for line in lines[-20:]:
        if line.strip():
            safe_print(f"     {line}")
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ pytest نصب شد")
    safe_print("  ✅ tests/test_ai.py")
    safe_print("  ✅ tests/test_scanner.py")
    safe_print("  ✅ tests/conftest.py")
    safe_print("  ✅ pytest.ini")
    safe_print("")
    safe_print("  🎯 دستور اجرا:")
    safe_print("     pytest tests/ -v")
    safe_print("     pytest tests/ --cov=. --cov-report=html")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
