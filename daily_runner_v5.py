# daily_runner_v5.py
# Smart_Bourse - Daily Runner
# اجرا: python daily_runner_v5.py

import os
import sys
import io
import json
import subprocess
from pathlib import Path
from datetime import datetime

# ✅ تنظیم UTF-8 برای CMD و IDLE
if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
except Exception:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")


def safe_print(text):
    """چاپ امن"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', errors='ignore').decode('ascii')
        print(safe_text)


def run_script(script_name, title):
    """اجرای اسکریپت با نمایش خطا"""
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  Ejraye {script_name}")
    safe_print("=" * 80)
    safe_print("")

    script = PROJECT_ROOT / script_name
    if not script.exists():
        safe_print(f"  ERR: {script_name} peyda nashod!")
        safe_print(f"  Masir: {script}")
        input("\n  Enter baraye bazgasht...")
        return

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
        )

        # نمایش خروجی
        if result.stdout:
            safe_print(result.stdout)

        # نمایش خطا
        if result.stderr:
            safe_print("=" * 80)
            safe_print("  ERR:")
            safe_print("=" * 80)
            safe_print(result.stderr)

        safe_print("")
        safe_print(f"  Exit code: {result.returncode}")

    except Exception as e:
        safe_print(f"  ERR: {e}")

    safe_print("")
    input("  Enter baraye bazgasht...")


def main():
    while True:
        # پاک کردن صفحه (اختیاری)
        # os.system('cls' if os.name == 'nt' else 'clear')

        safe_print("")
        safe_print("=" * 80)
        safe_print(f"  Smart_Bourse - Daily Runner v5")
        safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        safe_print("=" * 80)

        safe_print("")
        safe_print("  Gozine ra entekhab kon:")
        safe_print("")
        safe_print("  1. Tomorrow Picks (پیشنهاد فردا)  → tomorrow_v5.py")
        safe_print("  2. Full Scanner (اسکن کامل)       → smart_scanner_v5.py")
        safe_print("  3. School Mode (صبح خودکار)      → school_mode_v5.py")
        safe_print("  4. Khorooj")
        safe_print("")

        try:
            choice = input("  Shomare: ").strip()
        except KeyboardInterrupt:
            safe_print("\n  Khorooj...")
            break

        if choice == "1":
            run_script("tomorrow_v5.py", "Tomorrow Picks")
        elif choice == "2":
            run_script("smart_scanner_v5.py", "Full Scanner")
        elif choice == "3":
            run_script("school_mode_v5.py", "School Mode")
        elif choice == "4":
            safe_print("  Khorooj...")
            break
        else:
            safe_print("  ERR: Shomare namotabar")
            input("  Enter...")


if __name__ == "__main__":
    main()
