# install_fix_all.py
# پاکسازی و ساخت مجدد تسک‌ها (خودکار)
# اجرا: راست‌کلیک → Run as administrator

import os
import sys
import subprocess
import ctypes
from pathlib import Path

# تنظیم encoding
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


def is_admin():
    """چک ادمین"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def run(args):
    """اجرای دستور"""
    r = subprocess.run(
        args, capture_output=True, text=True,
        encoding='utf-8', errors='ignore', shell=True
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  🔧 پاکسازی و ساخت تسک‌های Smart_Bourse")
    safe_print("=" * 70)
    safe_print("")

    # ===== چک ادمین =====
    if not is_admin():
        safe_print("  ⚠️  ادمین نیستی!")
        safe_print("")
        safe_print("  📋 راه‌حل:")
        safe_print("     ۱. راست‌کلیک روی این فایل")
        safe_print("     ۲. Run as administrator")
        safe_print("     ۳. Yes")
        safe_print("")
        input("  Enter...")
        # تلاش برای اجرای خودکار به عنوان ادمین
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{__file__}"', None, 1
            )
            sys.exit(0)
        except:
            sys.exit(1)

    safe_print("  ✅ ادمین هستی!")
    safe_print("")

    PROJECT = Path(r"F:\python\har roz ba python\smart_bours")
    PYTHON = sys.executable
    V9 = PROJECT / "school_mode_v9.py"
    REFRESH = PROJECT / "refresh_ins_codes.py"

    # ===== چک فایل‌ها =====
    safe_print("📁 چک فایل‌ها...")
    if V9.exists():
        safe_print(f"   ✅ school_mode_v9.py")
    else:
        safe_print(f"   ❌ school_mode_v9.py پیدا نشد!")
        safe_print(f"      مسیر: {V9}")
        input("  Enter...")
        sys.exit(1)

    if REFRESH.exists():
        safe_print(f"   ✅ refresh_ins_codes.py")
    else:
        safe_print(f"   ⚠️  refresh_ins_codes.py نیست")

    safe_print("")

    # ===== کشتن پایتون‌ها =====
    safe_print("🔪 کشتن پروسه‌های پایتون...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"],
                       capture_output=True, shell=True)
        subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe"],
                       capture_output=True, shell=True)
    except:
        pass
    safe_print("   ✅ تمام")
    safe_print("")

    # ===== حذف تسک‌ها =====
    safe_print("🗑️  حذف تسک‌های قدیمی...")
    tasks = [
        "Smart_Bourse",
        "Smart_Bourse_v5",
        "Smart_Bourse_v7",
        "Smart_Bourse_v8",
        "Smart_Bourse_v9",
        "Smart_Bourse_Refresh",
        "Smart_Bourse_AutoRunner_Daily",
        "Smart_Bourse_AutoRunner_Logon",
    ]
    for t in tasks:
        code, out = run(f'schtasks /Delete /TN "{t}" /F')
        if "SUCCESS" in out:
            safe_print(f"   ✅ {t}: حذف شد")
        elif "cannot find" in out.lower():
            safe_print(f"   ⚠️  {t}: قبلاً نبود")
        else:
            safe_print(f"   ❓ {t}: {out.strip()[:40]}")

    safe_print("")

    # ===== ساخت تسک جدید v9 =====
    safe_print("📝 ساخت Smart_Bourse_v9 (8:45)...")
    tr_v9 = f'\\"{PYTHON}\\" \\"{V9}\\"'
    cmd_v9 = f'schtasks /Create /TN "Smart_Bourse_v9" /TR "{tr_v9}" /SC DAILY /ST 08:45 /F'
    code, out = run(cmd_v9)
    if "SUCCESS" in out:
        safe_print(f"   ✅ ساخته شد")
    else:
        safe_print(f"   ❌ خطا: {out.strip()[:80]}")
    safe_print("")

    # ===== ساخت تسک Refresh =====
    if REFRESH.exists():
        safe_print("📝 ساخت Smart_Bourse_Refresh (9:00)...")
        tr_ref = f'\\"{PYTHON}\\" \\"{REFRESH}\\"'
        cmd_ref = f'schtasks /Create /TN "Smart_Bourse_Refresh" /TR "{tr_ref}" /SC DAILY /ST 09:00 /F'
        code, out = run(cmd_ref)
        if "SUCCESS" in out:
            safe_print(f"   ✅ ساخته شد")
        else:
            safe_print(f"   ❌ خطا: {out.strip()[:80]}")
        safe_print("")

    # ===== چک نهایی =====
    safe_print("=" * 70)
    safe_print("  📊 چک نهایی")
    safe_print("=" * 70)
    code, out = run('schtasks /Query /FO LIST')
    found = []
    for line in out.split("\n"):
        if "Smart_Bourse" in line and "TaskName" in line:
            found.append(line.strip())
    if found:
        for f in found:
            safe_print(f"   ✅ {f}")
    else:
        safe_print("   ⚠️  هیچ تسکی پیدا نشد!")

    safe_print("")
    safe_print("=" * 70)
    safe_print("  🎉 تمام!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📌 فردا صبح ۸:۴۵ فقط v9 اجرا می‌شه.")
    safe_print("")

    input("  Enter برای خروج...")


if __name__ == "__main__":
    main()
    
