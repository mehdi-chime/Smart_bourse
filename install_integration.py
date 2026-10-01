# install_integration.py
# فاز ۹: ادغام AI با برنامه اصلی
# اجرا: python install_integration.py

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


# ═══════════════════════════════════════════════════════════
# ai_integration.py
# ═══════════════════════════════════════════════════════════

AI_INTEGRATION = '''"""
Project : Smart_Bourse
File    : ai_integration.py
Version : 1.0.0

Description :
    ادغام AI با برنامه اصلی
    استفاده در smart_bourse_v10 و اسکنرها
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_ai_advice(symbol, category, ratio, rsi=None, technical_score=None,
                  market_change_pct=None, last_price=None):
    """
    دریافت مشاوره AI برای یه سهم
    
    Returns:
        dict با کلیدهای: final_score, advice, confidence, mode
    """
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        
        return engine.advise(
            symbol=symbol,
            category=category,
            ratio=ratio,
            rsi=rsi,
            technical_score=technical_score,
            market_change_pct=market_change_pct,
            last_price=last_price,
        )
    except Exception as e:
        return {
            "symbol": symbol,
            "final_score": 50,
            "advice": f"AI error: {e}",
            "confidence": 0.5,
            "mode": "error",
        }


def record_ai_signal(symbol, category, ratio, rsi=None,
                     technical_score=None, last_price=None):
    """ثبت سیگنال در AI"""
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        
        today = datetime.now().strftime("%Y-%m-%d")
        engine.record_signal(
            trade_date=today,
            symbol=symbol,
            category=category,
            ratio=ratio,
            rsi=rsi,
            technical_score=technical_score,
            last_price=last_price,
        )
        return True
    except Exception:
        return False


def enhance_scanner_results(results):
    """
    غنی‌سازی نتایج اسکنر با AI
    
    Args:
        results: لیست نتایج اسکنر
    
    Returns:
        لیست غنی‌شده با AI
    """
    enhanced = []
    
    for r in results:
        try:
            symbol = r.get("symbol", "")
            ratio = r.get("ratio", 1)
            rsi = r.get("rsi")
            tech = r.get("score", 50)
            price = r.get("last")
            
            # مشاوره AI
            advice = get_ai_advice(
                symbol=symbol,
                category="SAFE_BUY",
                ratio=ratio,
                rsi=rsi,
                technical_score=tech,
                last_price=price,
            )
            
            # ترکیب
            r["ai_score"] = advice.get("final_score", 50)
            r["ai_advice"] = advice.get("advice", "")
            r["ai_confidence"] = advice.get("confidence", 0.5)
            r["ai_mode"] = advice.get("mode", "")
            
            # ثبت
            record_ai_signal(
                symbol=symbol,
                category="SAFE_BUY",
                ratio=ratio,
                rsi=rsi,
                technical_score=tech,
                last_price=price,
            )
            
            enhanced.append(r)
        except Exception:
            enhanced.append(r)
    
    return enhanced


def print_ai_summary():
    """خلاصه‌ی AI"""
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        engine.report()
    except Exception as e:
        print(f"AI error: {e}")


if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  🤖 تست AI Integration")
    print("=" * 80)
    print()
    
    # تست
    result = get_ai_advice(
        symbol="خگستر",
        category="SAFE_BUY",
        ratio=5.0,
        rsi=25,
        technical_score=70,
        market_change_pct=1.5,
        last_price=10000,
    )
    
    print("  مشاوره AI:")
    for k, v in result.items():
        print(f"     {k}: {v}")
    
    print()
    print("=" * 80)
    print("  ✅ تمام!")
    print("=" * 80)
    print()
'''


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🤖 فاز ۹: ادغام AI با برنامه اصلی")
    safe_print("=" * 80)
    safe_print("")

    # ۱. ساخت ai_integration.py
    safe_print("  📄 ساخت ai_integration.py...")
    size = write_file(PROJECT_ROOT / "ai_integration.py", AI_INTEGRATION)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۲. تست
    safe_print("  🧪 تست ai_integration...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "ai_integration.py")],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        encoding="utf-8",
        errors="ignore",
    )
    
    for line in result.stdout.split("\\n"):
        if line.strip():
            safe_print(f"     {line}")
    safe_print("")

    # ۳. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ ai_integration.py")
    safe_print("")
    safe_print("  🎯 دستور:")
    safe_print("     python ai_integration.py")
    safe_print("")
    safe_print("  📌 استفاده در اسکنر:")
    safe_print("     from ai_integration import enhance_scanner_results")
    safe_print("     results = enhance_scanner_results(results)")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
