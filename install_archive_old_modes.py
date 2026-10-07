# install_archive_old_modes.py
# آرشیو school_mode_v7 و v8
# اجرا: python install_archive_old_modes.py

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
ARCHIVE_DIR = PROJECT_ROOT / "_archive" / "school_mode_old"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  🗑️  آرشیو school_mode قدیمی")
    safe_print("=" * 70)
    safe_print("")

    # ساخت پوشه آرشیو
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    safe_print(f"📁 آرشیو: {ARCHIVE_DIR}")
    safe_print("")

    # فایل‌های قدیمی
    old_files = [
        PROJECT_ROOT / "school_mode_v7.py",
        PROJECT_ROOT / "school_mode_v8.py",
    ]

    # آرشیو
    for f in old_files:
        if f.exists():
            dest = ARCHIVE_DIR / f.name
            try:
                shutil.move(str(f), str(dest))
                safe_print(f"   ✅ آرشیو شد: {f.name} → {dest}")
            except Exception as e:
                safe_print(f"   ❌ خطا: {f.name} — {e}")
        else:
            safe_print(f"   ⚠️  نیست: {f.name}")

    safe_print("")

    # ===== حذف تسک‌های اضافی =====
    safe_print("🗑️  حذف تسک‌های اضافی...")

    tasks_to_delete = [
        "Smart_Bourse_AutoRunner_Logon",
        "Smart_Bourse_v5",
        "Smart_Bourse_v7",
        "Smart_Bourse_v8",
    ]

    for task in tasks_to_delete:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", task, "/F"],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            safe_print(f"   ✅ حذف: {task}")
        else:
            safe_print(f"   ⚠️  پیدا نشد: {task}")

    safe_print("")

    # ===== چک نهایی =====
    safe_print("🔍 چک نهایی تسک‌ها:")
    result = subprocess.run(
        ["schtasks", "/Query", "/FO", "LIST"],
        capture_output=True, text=True, encoding='utf-8', errors='ignore'
    )
    for line in result.stdout.split("\n"):
        if "Smart_Bourse" in line:
            safe_print(f"   {line.strip()}")

    safe_print("")

    # ===== چک فایل‌ها =====
    safe_print("🔍 چک فایل‌های school_mode:")
    for f in sorted(PROJECT_ROOT.glob("school_mode_v*.py")):
        safe_print(f"   ✅ {f.name}")

    safe_print("")
    safe_print("=" * 70)
    safe_print("  🎉 تمام!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📋 نتیجه:")
    safe_print("   - v7 و v8 آرشیو شدن")
    safe_print("   - تسک Logon حذف شد")
    safe_print("   - فقط v9 بمونه")
    safe_print("")


if __name__ == "__main__":
    main()
