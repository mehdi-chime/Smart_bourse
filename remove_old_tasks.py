# remove_old_tasks.py
# حذف تسک‌های قدیمی
# اجرا: python remove_old_tasks.py

import os
import sys
import subprocess

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🗑️ حذف تسک‌های قدیمی")
    safe_print("=" * 80)
    safe_print("")

    # ۱. اول ببین چی هست
    safe_print("  📋 لیست تسک‌های فعلی:")
    result = subprocess.run(
        ["schtasks", "/Query", "/FO", "LIST"],
        capture_output=True,
        text=True,
    )

    smart_tasks = []
    for line in result.stdout.split("\n"):
        if "Smart_Bourse" in line:
            task_name = line.strip().replace("TaskName:", "").strip()
            smart_tasks.append(task_name)
            safe_print(f"     {task_name}")

    safe_print("")

    # ۲. حذف همه (به جز v10)
    safe_print("  🗑️ حذف همه (به جز v10):")

    for task in smart_tasks:
        if "v10" in task:
            safe_print(f"     ✅ نگه دار: {task}")
            continue

        # حذف
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", task, "/F"],
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode == 0:
            safe_print(f"     ✅ حذف شد: {task}")
        else:
            safe_print(f"     ❌ خطا: {task}")

    safe_print("")

    # ۳. چک نهایی
    safe_print("  🔍 چک نهایی:")
    result = subprocess.run(
        ["schtasks", "/Query", "/FO", "LIST"],
        capture_output=True,
        text=True,
    )

    for line in result.stdout.split("\n"):
        if "Smart_Bourse" in line:
            safe_print(f"     {line.strip()}")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
