# create_install_school.py
# ساخت install_school_v3.py
# اجرا: python create_install_school.py

from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
TARGET = PROJECT_ROOT / "install_school_v3.py"

CODE = '''# install_school_v3.py
# نصب تسک خودکار v3
# اجرا: python install_school_v3.py

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\\python\\har roz ba python\\smart_bours")
PYTHON = sys.executable
SCRIPT = PROJECT_ROOT / "school_mode_v3.py"
TASK_NAME = "Smart_Bourse_v3"


def main():
    print()
    print("=" * 80)
    print("  🎓 نصب تسک Smart_Bourse v3")
    print("=" * 80)
    print()
    print(f"  Python: {PYTHON}")
    print(f"  Script: {SCRIPT}")
    print(f"  Task:   {TASK_NAME}")
    print()

    if not SCRIPT.exists():
        print(f"  ❌ {SCRIPT} پیدا نشد!")
        print(f"     اول school_mode_v3.py رو ذخیره کن")
        return

    # حذف تسک قدیمی
    subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True, shell=True
    )

    # نصب تسک
    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f\'"{PYTHON}" "{SCRIPT}"\',
        "/SC", "DAILY",
        "/ST", "08:45",
        "/F",
    ]

    print("  🚀 نصب...")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        print("  ✅ نصب شد!")
        print()
        print("  📅 زمان: هر روز 8:45")
        print()
        print("  📋 دستورات:")
        print(f"     schtasks /Run /TN {TASK_NAME}")
        print(f"     schtasks /Query /TN {TASK_NAME}")
        print(f"     schtasks /Delete /TN {TASK_NAME} /F")
    else:
        print(f"  ❌ خطا: {result.stderr}")

    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
'''

print()
print("=" * 80)
print("  📝 ساخت install_school_v3.py")
print("=" * 80)
print()

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(CODE)

print(f"  ✅ ذخیره شد: {TARGET}")
print(f"  📏 حجم: {TARGET.stat().st_size:,} بایت")
print()
print("  🎯 اجرا کن:")
print(f"     python install_school_v3.py")
print()
print("=" * 80)
print()
