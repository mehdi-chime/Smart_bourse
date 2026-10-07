# install_school_v10.py
# نصب تسک v10
# اجرا: python install_school_v10.py

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
SCRIPT = PROJECT_ROOT / "school_mode_v10.py"
TASK_NAME = "Smart_Bourse_v10"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🎓 نصب تسک Smart_Bourse v10")
    safe_print("=" * 80)
    safe_print("")

    if not SCRIPT.exists():
        safe_print(f"  ❌ {SCRIPT} پیدا نشد!")
        return

    safe_print(f"  📄 اسکریپت: {SCRIPT.name}")
    safe_print("")

    # حذف تسک‌های قبلی
    safe_print("  🗑️ حذف تسک‌های قدیمی...")

    old_tasks = [
        "Smart_Bourse_v9",
        "Smart_Bourse_Refresh",
        "Smart_Bourse_v8",
        "Smart_Bourse_v7",
        "Smart_Bourse",
    ]

    for task in old_tasks:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", task, "/F"],
            capture_output=True,
            text=True,
            shell=True,
        )
        if result.returncode == 0:
            safe_print(f"     ✅ حذف شد: {task}")
        else:
            safe_print(f"     ℹ️ نبود: {task}")
    safe_print("")

    # نصب v10
    safe_print("  🚀 نصب تسک v10...")

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON}" "{SCRIPT}"',
        "/SC", "DAILY",
        "/ST", "08:45",
        "/F",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        safe_print("  ✅ نصب شد!")
        safe_print(f"  📅 زمان: هر روز 8:45")
        safe_print(f"  🤖 داینامیک فعال")
    else:
        safe_print(f"  ❌ خطا: {result.stderr}")
    safe_print("")

    # چک نهایی
    safe_print("  🔍 چک نهایی...")
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        safe_print(f"     ✅ تسک نصب شده")
        for line in result.stdout.split("\n")[:6]:
            if line.strip():
                safe_print(f"     {line.strip()}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
