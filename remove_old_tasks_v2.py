# remove_old_tasks_v2.py
# حذف تسک‌های قدیمی — نسخه ۲ (با نمایش خطا)
# اجرا: python remove_old_tasks_v2.py

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
    safe_print("  🗑️ حذف تسک‌های قدیمی (نسخه ۲)")
    safe_print("=" * 80)
    safe_print("")

    # لیست تسک‌ها
    tasks_to_remove = [
        "\\Smart_Bourse_v9",
        "\\Smart_Bourse_Refresh",
        "Smart_Bourse_v9",
        "Smart_Bourse_Refresh",
    ]

    for task in tasks_to_remove:
        safe_print(f"  🗑️ حذف: {task}")

        cmd = ["schtasks", "/Delete", "/TN", task, "/F"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True,
        )

        safe_print(f"     Return code: {result.returncode}")

        if result.stdout:
            safe_print(f"     stdout: {result.stdout.strip()}")
        if result.stderr:
            safe_print(f"     stderr: {result.stderr.strip()}")

        safe_print("")

    # چک نهایی
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
