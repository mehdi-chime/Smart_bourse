# install_startup.py
# نصب school_mode_v7 در Startup ویندوز
# اجرا: python install_startup.py

import os
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
PYTHON = r"C:\Users\Mehdi\AppData\Local\Programs\Python\Python313\python.exe"
SCRIPT = PROJECT_ROOT / "school_mode_v7.py"

# پوشه Startup
STARTUP = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

# محتوای bat
BAT_CONTENT = f'''@echo off
chcp 65001 >nul
title Smart_Bourse v7
cd /d "{PROJECT_ROOT}"
"{PYTHON}" "{SCRIPT}"
'''


def main():
    print()
    print("=" * 80)
    print("  Install Startup - Smart_Bourse v7")
    print("=" * 80)
    print()

    print(f"  Startup Folder: {STARTUP}")
    print(f"  Script: {SCRIPT}")
    print()

    if not STARTUP.exists():
        print(f"  ❌ Startup folder peyda nashod!")
        return

    if not SCRIPT.exists():
        print(f"  ❌ {SCRIPT} peyda nashod!")
        return

    # ساخت bat
    bat_file = STARTUP / "Smart_Bourse.bat"
    with open(bat_file, "w", encoding="utf-8") as f:
        f.write(BAT_CONTENT)

    print(f"  ✅ ذخیره شد: {bat_file}")
    print()
    print("  🎯 حالا:")
    print("     ۱. کامپیوتر که روشن شد")
    print("     ۲. Smart_Bourse v7 خودکار اجرا میشه")
    print("     ۳. پیام شروع به ایتا میاد")
    print("     ۴. منتظر 8:45 میمونه")
    print("     ۵. اسکن میکنه")
    print("     ۶. پیام کامل به ایتا")
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
