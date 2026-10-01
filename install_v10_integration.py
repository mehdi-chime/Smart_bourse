# install_v10_integration.py
# فاز ۱۶: ادغام AI با smart_bourse_v10
# اجرا: python install_v10_integration.py

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


def add_ai_to_v10():
    """اضافه کردن AI به smart_bourse_v10.py"""
    v10_file = PROJECT_ROOT / "smart_bourse_v10.py"
    
    if not v10_file.exists():
        safe_print("  ❌ smart_bourse_v10.py پیدا نشد!")
        return False
    
    content = v10_file.read_text(encoding="utf-8")
    
    # چک تکراری
    if "AI_INTEGRATION" in content:
        safe_print("  ℹ️ AI از قبل ادغام شده")
        return True
    
    # اضافه کردن import
    if "from ai_integration import" not in content:
        # پیدا کردن جایی برای اضافه کردن
        import_marker = "import numpy as np"
        if import_marker in content:
            content = content.replace(
                import_marker,
                import_marker + "\n\n# AI Integration\ntry:\n    from ai_integration import get_ai_advice, record_ai_signal\n    AI_AVAILABLE = True\nexcept ImportError:\n    AI_AVAILABLE = False"
            )
    
    # اضافه کردن AI به print_analysis
    ai_section = '''
    # AI Analysis
    if AI_AVAILABLE:
        try:
            ai_result = get_ai_advice(
                symbol=r.get('symbol', ''),
                category='SAFE_BUY',
                ratio=1.0,
                rsi=r.get('rsi'),
                technical_score=r.get('percent', 50),
                last_price=r.get('last'),
            )
            safe_print("")
            safe_print(f"  🤖 AI Analysis:")
            safe_print(f"     Final Score: {ai_result.get('final_score')}")
            safe_print(f"     Advice: {ai_result.get('advice')}")
            safe_print(f"     Confidence: {ai_result.get('confidence')}")
            safe_print(f"     Mode: {ai_result.get('mode')}")
        except Exception as e:
            pass
'''
    
    # پیدا کردن "تصمیم نهایی" و اضافه کردن AI بعدش
    marker = "# ۵. قیمت‌های معاملاتی"
    if marker in content:
        content = content.replace(marker, ai_section + "\n    " + marker)
    
    v10_file.write_text(content, encoding="utf-8")
    safe_print("  ✅ AI به smart_bourse_v10.py اضافه شد")
    return True


def test_v10():
    """تست v10"""
    safe_print("")
    safe_print("  🧪 تست import...")
    
    try:
        import importlib
        if "smart_bourse_v10" in sys.modules:
            importlib.reload(sys.modules["smart_bourse_v10"])
        
        import smart_bourse_v10
        safe_print("     ✅ import موفق")
        
        # چک AI
        if hasattr(smart_bourse_v10, "AI_AVAILABLE"):
            safe_print(f"     AI Available: {smart_bourse_v10.AI_AVAILABLE}")
    except Exception as e:
        safe_print(f"     ⚠️ {e}")
    safe_print("")


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🤖 فاز ۱۶: ادغام AI با smart_bourse_v10")
    safe_print("=" * 80)
    safe_print("")

    # ۱. ادغام
    safe_print("  🔧 ادغام AI...")
    add_ai_to_v10()
    safe_print("")

    # ۲. تست
    test_v10()
    safe_print("")

    # ۳. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ AI به smart_bourse_v10.py اضافه شد")
    safe_print("")
    safe_print("  🎯 حالا smart_bourse_v10 از AI استفاده می‌کنه")
    safe_print("")
    safe_print("  📌 تست:")
    safe_print("     python smart_bourse_v10.py")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
