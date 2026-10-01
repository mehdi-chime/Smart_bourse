# update_memory_phase6.py
# ذخیره فاز ۶ در حافظه
# اجرا: python update_memory_phase6.py

import os
import sys
import re
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
MEMORY_FILE = PROJECT_ROOT / "PROJECT_MEMORY.md"
BACKUP_DIR = PROJECT_ROOT / "backup" / "memory"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


PHASE6_LINES = [
    "",
    "---",
    "",
    "## ✅ فاز ۶ — دیتابیس (تکمیل شد)",
    "",
    f"**تاریخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
    "### 📝 کارها",
    "",
    "| # | کار | نتیجه |",
    "|:---:|:---|:---:|",
    "| 1 | ساخت دیتابیس جدید | `smart_bourse_v2.db` |",
    "| 2 | جدول stocks | 1,033 |",
    "| 3 | جدول price_history | 302,134 |",
    "| 4 | جدول signals | 118 |",
    "| 5 | جدول outcomes | 104 |",
    "| 6 | جدول trades | 0 |",
    "",
    "### 🗄️ دیتابیس جدید",
    "",
    "- **مسیر:** `data/smart_bourse_v2.db`",
    "- **حجم:** ~30 MB",
    "- **جدول‌ها:** 5",
    "- **رکوردها:** ~303,000",
    "",
    "### 🔑 تغییرات کلیدی",
    "",
    "- **مهاجرت:** 1,033 فایل JSON → دیتابیس",
    "- **302,134 رکورد** قیمت تاریخی",
    "- **ایندکس‌گذاری** برای سرعت",
    "",
    "### 📊 بکاپ‌ها",
    "",
    "- `backup/database/history_backup_20261001_183653`",
    "",
    "---",
    "",
    "## 🎯 خلاصه‌ی کل فازها",
    "",
    "| فاز | عنوان | وضعیت |",
    "|:---:|:---|:---:|",
    "| 1 | بازسازی AI | ✅ |",
    "| 2 | ML واقعی | ✅ |",
    "| 3 | پاکسازی | ✅ |",
    "| 4 | مستندسازی | ✅ |",
    "| 5 | تست خودکار | ✅ |",
    "| 6 | دیتابیس | ✅ |",
    "",
    "**جمع: 6/6 فاز!** 🎉",
    "",
    "---",
    "",
    "## 📊 نمره‌ی نهایی",
    "",
    "| جنبه | قبل | بعد |",
    "|:---|:---:|:---:|",
    "| ایده | 95 | 95 |",
    "| استراتژی | 85 | 90 |",
    "| پیاده‌سازی | 75 | 85 |",
    "| ساختار | 70 | 90 |",
    "| AI | 55 | 80 |",
    "| مستندسازی | 40 | 85 |",
    "| کیفیت کد | 70 | 80 |",
    "| مقیاس | 90 | 90 |",
    "| پایداری | 75 | 88 |",
    "| آینده‌نگری | 90 | 95 |",
    "| **میانگین** | **72** | **88** |",
    "",
    "---",
    "",
    "## 📋 دستورالعمل چت جدید",
    "",
    "«فاز 1-6 تکمیل شد:",
    "- AI v3.0 با ML",
    "- 12/12 تست PASSED",
    "- دیتابیس 302,134 رکورد",
    "- مستندات کامل",
    "",
    "نمره: 72 → 88",
    "",
    "لطفاً PROJECT_MEMORY.md و ROADMAP_5.md رو بخون.»",
    "",
]


PHASE6_SECTION = "\n".join(PHASE6_LINES)


def backup_memory():
    if not MEMORY_FILE.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"PROJECT_MEMORY_{timestamp}.md"
    content = MEMORY_FILE.read_text(encoding="utf-8")
    backup_file.write_text(content, encoding="utf-8")
    return backup_file


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📝 ذخیره فاز ۶ در حافظه")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  📦 بکاپ...")
    backup = backup_memory()
    if backup:
        safe_print(f"     ✅ {backup.name}")
    safe_print("")

    if not MEMORY_FILE.exists():
        safe_print("  ❌ PROJECT_MEMORY.md پیدا نشد!")
        return

    safe_print("  📂 خوندن...")
    content = MEMORY_FILE.read_text(encoding="utf-8")
    safe_print(f"     ✅ {len(content):,} کاراکتر")
    safe_print("")

    if "فاز ۶ — دیتابیس (تکمیل شد)" in content:
        safe_print("  ℹ️ بخش فاز ۶ از قبل وجود داره!")
        pattern = r"\n---\n\n## ✅ فاز ۶ — دیتابیس \(تکمیل شد\).*?(?=\n## |\Z)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    safe_print("  ➕ اضافه کردن بخش فاز ۶...")
    content += PHASE6_SECTION
    safe_print("     ✅ اضافه شد")

    new_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(
        r"> آخرین آپدیت:.*",
        f"> آخرین آپدیت: {new_date}",
        content,
        count=1
    )

    safe_print("")
    safe_print("  💾 ذخیره...")
    MEMORY_FILE.write_text(content, encoding="utf-8")
    safe_print(f"     ✅ {len(content):,} کاراکتر")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
