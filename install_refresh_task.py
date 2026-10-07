# install_refresh_task.py
# نصب تسک روزانه برای refresh_ins_codes
# اجرا: python install_refresh_task.py

import os
import sys
import subprocess
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
PYTHON = sys.executable
SCRIPT = PROJECT_ROOT / "refresh_ins_codes.py"
TASK_NAME = "Smart_Bourse_Refresh"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📅 نصب تسک Refresh روزانه")
    safe_print("=" * 80)
    safe_print("")

    if not SCRIPT.exists():
        safe_print(f"  ❌ {SCRIPT} پیدا نشد!")
        safe_print("  اول `refresh_ins_codes.py` رو بساز!")
        return

    safe_print(f"  📄 اسکریپت: {SCRIPT.name}")
    safe_print(f"  🐍 پایتون: {PYTHON}")
    safe_print("")

    # حذف تسک قبلی
    safe_print("  🗑️ حذف تسک قبلی (اگه هست)...")
    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True,
        text=True,
        shell=True,
    )
    if result.returncode == 0:
        safe_print("     ✅ حذف شد")
    else:
        safe_print("     ℹ️ تسک قبلی نبود")
    safe_print("")

    # نصب جدید
    safe_print("  🚀 نصب تسک جدید...")

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON}" "{SCRIPT}"',
        "/SC", "DAILY",
        "/ST", "09:00",
        "/F",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        safe_print("  ✅ نصب شد!")
        safe_print("  📅 زمان: هر روز 9:00")
        safe_print("  📌 کار: استخراج مجدد INS Codeها")
        safe_print("")
        safe_print("  📋 دستورات:")
        safe_print(f"     schtasks /Query /TN {TASK_NAME}")
        safe_print(f"     schtasks /Run /TN {TASK_NAME}")
        safe_print(f"     schtasks /Delete /TN {TASK_NAME} /F")
    else:
        safe_print(f"  ❌ خطا: {result.stderr}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
