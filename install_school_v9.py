# install_school_v9.py
# نصب تسک v9
# اجرا: python install_school_v9.py

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
PYTHON = sys.executable
SCRIPT = PROJECT_ROOT / "school_mode_v9.py"
TASK_NAME = "Smart_Bourse_v9"


def main():
    print()
    print("=" * 80)
    print("  🎓 نصب تسک Smart_Bourse v9")
    print("=" * 80)
    print()

    if not SCRIPT.exists():
        print(f"  ❌ {SCRIPT} پیدا نشد!")
        return

    # حذف تسک‌های قبلی
    for old in ["Smart_Bourse_v5", "Smart_Bourse_v7", "Smart_Bourse_v8", "Smart_Bourse"]:
        subprocess.run(
            ["schtasks", "/Delete", "/TN", old, "/F"],
            capture_output=True,
            shell=True,
        )

    # نصب v9
    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON}" "{SCRIPT}"',
        "/SC", "DAILY",
        "/ST", "08:45",
        "/F",
    ]

    print("  🚀 نصب...")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        print("  ✅ نصب شد!")
        print(f"  📅 زمان: هر روز 8:45")
        print(f"  🤖 AI فعال")
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
