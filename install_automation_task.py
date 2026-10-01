"""
Project : Smart_Bourse
File    : install_automation_task.py
Version : 1.0.0

Description :
    نصب تسک زمان‌بند برای daily_ai_runner
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
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
