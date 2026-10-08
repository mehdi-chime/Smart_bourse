# upgrade_v10_auto.py
# ارتقای v10 — اضافه کردن alert_manager + update_portfolio
# اجرا: python upgrade_v10_auto.py

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
V10_FILE = PROJECT_ROOT / "school_mode_v10.py"
BACKUP_DIR = PROJECT_ROOT / "backup" / "v10"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 ارتقای v10")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    if not V10_FILE.exists():
        safe_print(f"  ❌ {V10_FILE} پیدا نشد!")
        return

    # ۱. بکاپ
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"school_mode_v10_{timestamp}.py"

    content = V10_FILE.read_text(encoding="utf-8")
    backup.write_text(content, encoding="utf-8")
    safe_print(f"  📦 بکاپ: {backup.name}")
    safe_print("")

    # ۲. چک تکراری
    if "alert_manager" in content and "update_portfolio" in content:
        safe_print("  ℹ️ از قبل اضافه شده!")
        return

    # ۳. اضافه کردن تابع
    new_functions = '''

def run_alert_manager():
    """اجرای هشدار خودکار"""
    log("Ejraye alert_manager...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "alert_manager.py")],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='ignore',
        )
        log(f"   exit: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        log(f"   ERR: {e}")
        return False


def run_update_portfolio():
    """اجرای رصد پرتفوی"""
    log("Ejraye update_portfolio...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "update_portfolio.py")],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='ignore',
        )
        log(f"   exit: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        log(f"   ERR: {e}")
        return False

'''

    # اضافه کن قبل از main
    if "def main():" in content:
        content = content.replace("def main():", new_functions + "\ndef main():", 1)
        safe_print("  ✅ تابع‌ها اضافه شدن")
    else:
        safe_print("  ❌ تابع main پیدا نشد!")
        return

    # ۴. اضافه کردن به حلقه
    # پیدا کردن آخرین send
    loop_add = '''
            # ۶. هشدار خودکار
            run_alert_manager()

            # ۷. رصد پرتفوی
            run_update_portfolio()

'''

    # اضافه کن قبل از time.sleep(60)
    if "time.sleep(60)" in content:
        content = content.replace("time.sleep(60)", loop_add + "        time.sleep(60)", 1)
        safe_print("  ✅ به حلقه اضافه شد")
    else:
        safe_print("  ❌ حلقه پیدا نشد!")
        return

    # ۵. ذخیره
    V10_FILE.write_text(content, encoding="utf-8")
    safe_print("")
    safe_print(f"  💾 ذخیره: {V10_FILE}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
