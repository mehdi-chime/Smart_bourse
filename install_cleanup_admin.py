# install_cleanup_admin.py
# پاکسازی کامل + ساخت مجدد تسک‌ها (خودکار)
# اجرا: راست‌کلیک → Run as administrator
# یا: python install_cleanup_admin.py

import os
import sys
import subprocess
import ctypes
from pathlib import Path
from datetime import datetime

# تنظیم encoding
if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
PYTHON_EXE = sys.executable
SCHOOL_V9 = PROJECT_ROOT / "school_mode_v9.py"
REFRESH = PROJECT_ROOT / "refresh_ins_codes.py"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def is_admin():
    """چک کن ادمین هست یا نه"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def run_cmd(args):
    """اجرای دستور CMD"""
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        shell=True
    )
    return result.returncode, result.stdout, result.stderr


def delete_task(task_name):
    """حذف تسک"""
    code, out, err = run_cmd(f'schtasks /Delete /TN "{task_name}" /F')
    if code == 0:
        return True, "حذف شد"
    elif "cannot find" in (out + err).lower():
        return True, "قبلاً نبود"
    else:
        return False, (out + err)[:60]


def create_task(task_name, script_path, time_str):
    """ساخت تسک"""
    cmd = f'schtasks /Create /TN "{task_name}" /TR "\\"{PYTHON_EXE}\\" \\"{script_path}\\"" /SC DAILY /ST {time_str} /F'
    code, out, err = run_cmd(cmd)
    if code == 0:
        return True, "ساخته شد"
    else:
        return False, (out + err)[:80]


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  🔧 پاکسازی کامل تسک‌ها")
    safe_print("=" * 70)
    safe_print("")

    # ===== چک ادمین =====
    if not is_admin():
        safe_print("  ❌ این فایل باید با دسترسی **ادمین** اجرا بشه!")
        safe_print("")
        safe_print("  📋 روش:")
        safe_print("     ۱. راست‌کلیک روی این فایل")
        safe_print("     ۲. Run as administrator")
        safe_print("     ۳. Yes")
        safe_print("")
        safe_print("  یا:")
        safe_print("     توی CMD ادمین: python install_cleanup_admin.py")
        safe_print("")
        input("  Enter برای خروج...")
        sys.exit(1)

    safe_print("  ✅ ادمین هستی!")
    safe_print("")

    # ===== چک فایل‌ها =====
    safe_print("📁 چک فایل‌ها...")
    if SCHOOL_V9.exists():
        safe_print(f"   ✅ school_mode_v9.py ({SCHOOL_V9.stat().st_size:,} bytes)")
    else:
        safe_print(f"   ❌ school_mode_v9.py پیدا نشد!")
        sys.exit(1)

    if REFRESH.exists():
        safe_print(f"   ✅ refresh_ins_codes.py")
    else:
        safe_print(f"   ⚠️  refresh_ins_codes.py نیست (اختیاری)")
    safe_print("")

    # ===== کشتن python ها =====
    safe_print("🔪 کشتن پروسه‌های پایتون...")
    run_cmd("taskkill /F /IM python.exe")
    run_cmd("taskkill /F /IM pythonw.exe")
    safe_print("   ✅ تمام پروسه‌ها کشته شدن")
    safe_print("")

    # ===== حذف تسک‌های قدیمی =====
    safe_print("🗑️  حذف تسک‌های قدیمی...")
    tasks_to_delete = [
        "Smart_Bourse",
        "Smart_Bourse_v5",
        "Smart_Bourse_v7",
        "Smart_Bourse_v8",
        "Smart_Bourse_v9",
        "Smart_Bourse_Refresh",
        "Smart_Bourse_AutoRunner_Daily",
        "Smart_Bourse_AutoRunner_Logon",
    ]
    for t in tasks_to_delete:
        ok, msg = delete_task(t)
        if ok:
            safe_print(f"   ✅ {t}: {msg}")
        else:
            safe_print(f"   ❌ {t}: {msg}")
    safe_print("")

    # ===== ساخت تسک‌های جدید =====
    safe_print("📝 ساخت تسک‌های جدید...")

    # v9
    ok, msg = create_task("Smart_Bourse_v9", SCHOOL_V9, "08:45")
    if ok:
        safe_print(f"   ✅ Smart_Bourse_v9 (8:45)")
    else:
        safe_print(f"   ❌ Smart_Bourse_v9: {msg}")

    # Refresh
    if REFRESH.exists():
        ok, msg = create_task("Smart_Bourse_Refresh", REFRESH, "09:00")
        if ok:
            safe_print(f"   ✅ Smart_Bourse_Refresh (9:00)")
        else:
            safe_print(f"   ❌ Smart_Bourse_Refresh: {msg}")
    safe_print("")

    # ===== چک نهایی =====
    safe_print("🔍 چک نهایی...")
    code, out, err = run_cmd('schtasks /Query /FO LIST')
    found = []
    for line in out.split("\n"):
        if "Smart_Bourse" in line:
            found.append(line.strip())

    if found:
        for f in found:
            safe_print(f"   {f}")
    else:
        safe_print("   ⚠️  هیچ تسکی پیدا نشد!")
    safe_print("")

    # ===== نتیجه =====
    safe_print("=" * 70)
    safe_print("  🎉 تمام!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📋 نتیجه:")
    safe_print("   • پروسه‌های پایتون کشته شدن")
    safe_print("   • تسک‌های قدیمی حذف شدن")
    safe_print(f"   • تسک‌های جدید ساخته شدن")
    safe_print("   • فقط v9 و Refresh باقی موندن")
    safe_print("")
    safe_print("📌 فردا صبح ۸:۴۵ خودکار اجرا می‌شه.")
    safe_print("")

    input("  Enter برای خروج...")


if __name__ == "__main__":
    main()
