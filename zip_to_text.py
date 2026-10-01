# zip_to_text.py
# تبدیل ZIP به فایل متنی
# اجرا: python zip_to_text.py

import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
ZIP_FILE = PROJECT_ROOT / "for_deepseek_20261001_0240.zip"
OUTPUT_FILE = PROJECT_ROOT / "for_deepseek_all.txt"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📦 تبدیل ZIP به فایل متنی")
    safe_print("=" * 80)
    safe_print("")

    if not ZIP_FILE.exists():
        safe_print(f"  ❌ ZIP پیدا نشد: {ZIP_FILE}")
        return

    safe_print(f"  📂 باز کردن ZIP...")

    with zipfile.ZipFile(ZIP_FILE, 'r') as z:
        files = z.namelist()
        safe_print(f"  ✅ {len(files)} فایل پیدا شد")
        safe_print("")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            out.write("=" * 100 + "\n")
            out.write("  محتوای کامل پروژه Smart_Bourse\n")
            out.write(f"  تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"  تعداد فایل‌ها: {len(files)}\n")
            out.write("=" * 100 + "\n\n")

            for i, name in enumerate(files, 1):
                # فقط فایل‌های متنی
                if not name.endswith(('.py', '.txt', '.md', '.json', '.log', '.bat', '.html', '.csv')):
                    continue

                try:
                    content = z.read(name).decode('utf-8', errors='ignore')

                    out.write("\n" + "=" * 100 + "\n")
                    out.write(f"  فایل {i}: {name}\n")
                    out.write("=" * 100 + "\n\n")
                    out.write(content)
                    out.write("\n\n")

                    safe_print(f"  ✅ {name}")

                except Exception as e:
                    safe_print(f"  ❌ {name}: {e}")

    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  ✅ تمام!")
    safe_print(f"  📁 خروجی: {OUTPUT_FILE}")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
