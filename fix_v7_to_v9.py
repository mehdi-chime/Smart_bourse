# fix_v7_to_v9.py
# حذف تسک v7 و نصب v9
# اجرا: python fix_v7_to_v9.py

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
SCRIPT = PROJECT_ROOT / "school_mode_v9.py"
TASK_NAME = "Smart_Bourse_v9"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔧 حذف v7 و نصب v9")
    safe_print("=" * 80)
    safe_print("")

    # ۱. حذف همه تسک‌های قبلی
    safe_print("  🗑️ حذف تسک‌های قبلی...")

    old_tasks = [
        "Smart_Bourse_v3",
        "Smart_Bourse_v5",
        "Smart_Bourse_v7",
        "Smart_Bourse_v8",
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

    # ۲. چک school_mode_v9.py
    safe_print("  🔍 چک school_mode_v9.py...")
    if not SCRIPT.exists():
        safe_print(f"     ❌ {SCRIPT} پیدا نشد!")
        return
    safe_print(f"     ✅ موجود")

    # ۳. چک اسکنر
    content = SCRIPT.read_text(encoding="utf-8")
    if "smart_scanner_v8.py" in content:
        safe_print("     ✅ از v8 استفاده می‌کنه")
    elif "smart_scanner_v5.py" in content:
        safe_print("     ⚠️ از v5 استفاده می‌کنه!")
        content = content.replace("smart_scanner_v5.py", "smart_scanner_v8.py")
        SCRIPT.write_text(content, encoding="utf-8")
        safe_print("     ✅ v5 → v8 اصلاح شد")
    else:
        safe_print("     ⚠️ اسکنر پیدا نشد")
    safe_print("")

    # ۴. نصب v9
    safe_print("  🚀 نصب تسک v9...")

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
        safe_print("     ✅ نصب شد!")
        safe_print(f"     📅 زمان: هر روز 8:45")
        safe_print(f"     🤖 AI فعال")
    else:
        safe_print(f"     ❌ خطا: {result.stderr}")
    safe_print("")

    # ۵. چک نهایی
    safe_print("  🔍 چک نهایی...")
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        safe_print(f"     ✅ تسک نصب شده")
        for line in result.stdout.split("\n")[:8]:
            if line.strip():
                safe_print(f"     {line.strip()}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
