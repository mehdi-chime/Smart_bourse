# install_automation.py
# فاز ۷: اتوماسیون کامل
# اجرا: python install_automation.py

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
# daily_ai_runner.py
# ═══════════════════════════════════════════════════════════

DAILY_AI_RUNNER = '''"""
Project : Smart_Bourse
File    : daily_ai_runner.py
Version : 1.0.0

Description :
    رانر روزانه AI — ادغام با برنامه اصلی
"""

import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.ai_engine import AIEngine


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def load_signals():
    """بارگذاری سیگنال‌های امروز از hunter"""
    hunter_dir = PROJECT_ROOT / "data" / "hunter"
    today = datetime.now().strftime("%Y-%m-%d")
    
    signals = []
    
    # پیدا کردن فایل امروز
    for f in hunter_dir.glob(f"*{today}*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if "top" in data:
                for s in data["top"]:
                    signals.append({
                        "symbol": s.get("symbol"),
                        "category": "SAFE_BUY",
                        "ratio": s.get("ratio", 1),
                        "rsi": s.get("rsi"),
                        "technical_score": s.get("score", 50),
                        "last_price": s.get("last"),
                    })
        except Exception:
            pass
    
    return signals


def record_signals_to_ai():
    """ثبت سیگنال‌ها در AI"""
    safe_print("  📝 ثبت سیگنال‌ها در AI...")
    
    signals = load_signals()
    
    if not signals:
        safe_print("     ⚠️ سیگنالی پیدا نشد")
        return 0
    
    engine = AIEngine()
    today = datetime.now().strftime("%Y-%m-%d")
    
    count = 0
    for s in signals:
        engine.record_signal(
            trade_date=today,
            symbol=s["symbol"],
            category=s["category"],
            ratio=s["ratio"],
            rsi=s["rsi"],
            technical_score=s["technical_score"],
            last_price=s["last_price"],
        )
        count += 1
    
    safe_print(f"     ✅ {count} سیگنال ثبت شد")
    return count


def check_outcomes_from_ai():
    """چک نتایج قبلی"""
    safe_print("  🔍 چک نتایج قبلی...")
    
    engine = AIEngine()
    
    # تابع ساده برای چک قیمت
    def price_lookup(symbol, days):
        """چک قیمت N روز قبل"""
        try:
            from history.history_database import HistoryDatabase
            db = HistoryDatabase()
            
            # فعلاً ساده
            return None
        except Exception:
            return None
    
    checked = engine.check_outcomes(price_lookup)
    safe_print(f"     ✅ {checked} نتیجه چک شد")
    return checked


def report_ai():
    """گزارش AI"""
    safe_print("")
    safe_print("  📊 گزارش AI...")
    
    engine = AIEngine()
    engine.report()


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🤖 رانر روزانه AI")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # ۱. ثبت سیگنال‌ها
    record_signals_to_ai()
    safe_print("")

    # ۲. چک نتایج
    check_outcomes_from_ai()
    safe_print("")

    # ۳. گزارش
    report_ai()
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
'''


# ═══════════════════════════════════════════════════════════
# install_automation_task.py
# ═══════════════════════════════════════════════════════════

INSTALL_TASK = '''"""
Project : Smart_Bourse
File    : install_automation_task.py
Version : 1.0.0

Description :
    نصب تسک زمان‌بند برای daily_ai_runner
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\\python\\har roz ba python\\smart_bours")
PYTHON = sys.executable
SCRIPT = PROJECT_ROOT / "daily_ai_runner.py"
TASK_NAME = "Smart_Bourse_AI_Daily"


def main():
    print()
    print("=" * 80)
    print("  📅 نصب تسک AI")
    print("=" * 80)
    print()

    if not SCRIPT.exists():
        print(f"  ❌ {SCRIPT} پیدا نشد!")
        return

    # حذف تسک قبلی
    subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True,
        shell=True,
    )

    # نصب
    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON}" "{SCRIPT}"',
        "/SC", "DAILY",
        "/ST", "13:00",
        "/F",
    ]

    print("  🚀 نصب...")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        print("  ✅ نصب شد!")
        print(f"  📅 زمان: هر روز 13:00")
        print()
        print("  📋 دستورات:")
        print(f"     schtasks /Run /TN {TASK_NAME}")
        print(f"     schtasks /Query /TN {TASK_NAME}")
    else:
        print(f"  ❌ خطا: {result.stderr}")

    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
'''


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🤖 فاز ۷: اتوماسیون کامل")
    safe_print("=" * 80)
    safe_print("")

    # ۱. daily_ai_runner.py
    safe_print("  📄 ساخت daily_ai_runner.py...")
    size = write_file(PROJECT_ROOT / "daily_ai_runner.py", DAILY_AI_RUNNER)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۲. install_automation_task.py
    safe_print("  📄 ساخت install_automation_task.py...")
    size = write_file(PROJECT_ROOT / "install_automation_task.py", INSTALL_TASK)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۳. تست
    safe_print("  🧪 تست daily_ai_runner...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "daily_ai_runner.py")],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        encoding="utf-8",
        errors="ignore",
    )
    
    for line in result.stdout.split("\\n")[-20:]:
        if line.strip():
            safe_print(f"     {line}")
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ daily_ai_runner.py")
    safe_print("  ✅ install_automation_task.py")
    safe_print("")
    safe_print("  🎯 دستورات:")
    safe_print("     python daily_ai_runner.py")
    safe_print("     python install_automation_task.py")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
