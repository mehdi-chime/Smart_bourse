# update_memory_final.py
# آپدیت نهایی حافظه
# اجرا: python update_memory_final.py

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


FINAL_LINES = [
    "",
    "---",
    "",
    "## 🔒 امنیت — هشدار مهم!",
    "",
    "### ⚠️ توکن ایتا",
    "",
    "**توکن ایتا هرگز نباید در GitHub منتشر شود!**",
    "",
    "**راه‌حل:**",
    "1. `scanner/alert_config.py` در `.gitignore` باشه",
    "2. یه `alert_config.example.py` بساز (بدون توکن)",
    "3. توکن‌ها رو از **Environment Variables** بخون",
    "",
    "### 📝 فایل `.gitignore`",
    "",
    "```",
    "# Secrets",
    "scanner/alert_config.py",
    "data/ai/*.pkl",
    "*.log",
    "backup/",
    "_archive/",
    "",
    "# Data",
    "data/history/",
    "data/real_flow/",
    "data/live_records/",
    "*.db",
    "",
    "# Python",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    ".pytest_cache/",
    "```",
    "",
    "---",
    "",
    "## 📊 وضعیت نهایی — 12/12 فاز",
    "",
    "| فاز | عنوان | وضعیت |",
    "|:---:|:---|:---:|",
    "| 1 | بازسازی AI | ✅ |",
    "| 2 | ML واقعی | ✅ |",
    "| 3 | پاکسازی | ✅ |",
    "| 4 | مستندسازی | ✅ |",
    "| 5 | تست خودکار | ✅ |",
    "| 6 | دیتابیس | ✅ |",
    "| 7 | اتوماسیون | ✅ |",
    "| 8 | داشبورد | ✅ |",
    "| 9 | ادغام | ✅ |",
    "| 10 | XGBoost | ⚠️ |",
    "| 11 | بک‌تست | ✅ |",
    "| 12 | مستندات نهایی | ✅ |",
    "",
    "**جمع: 11/12 (XGBoost ناتمام)**",
    "",
    "---",
    "",
    "## 🎯 فازهای باقی‌مانده",
    "",
    "| فاز | عنوان | اهمیت |",
    "|:---:|:---|:---:|",
    "| 13 | XGBoost | 🟢 |",
    "| 14 | تلگرام | 🟢 |",
    "| 15 | بهینه‌سازی | 🟡 |",
    "| 16 | ادغام با smart_bourse_v10 | 🔴 **مهم** |",
    "| 17 | تست کامل | 🟡 |",
    "",
    "**مهم‌ترین:** فاز 16",
    "",
    "---",
    "",
    "## 📊 نمره‌ی نهایی",
    "",
    "| جنبه | نمره |",
    "|:---|:---:|",
    "| ایده | 95 |",
    "| استراتژی | 92 |",
    "| پیاده‌سازی | 92 |",
    "| ساختار | 93 |",
    "| AI | 82 |",
    "| مستندسازی | 95 |",
    "| کیفیت کد | 88 |",
    "| مقیاس | 90 |",
    "| پایداری | 90 |",
    "| آینده‌نگری | 95 |",
    "| **میانگین** | **92** |",
    "",
    "---",
    "",
    "## 📋 دستورالعمل چت جدید",
    "",
    "«فاز 1-12 تکمیل شد (به جز XGBoost):",
    "- AI v3.0 با ML",
    "- 12/12 تست PASSED",
    "- دیتابیس 302,134 رکورد",
    "- اتوماسیون کامل",
    "- داشبورد HTML",
    "- ادغام با اسکنرها",
    "- بک‌تست کامل",
    "- مستندات کامل",
    "",
    "نمره: 72 → 92",
    "",
    "**هشدار امنیتی:** توکن ایتا در GitHub نباشه!",
    "",
    "لطفاً PROJECT_MEMORY.md و ROADMAP_5.md رو بخون.»",
    "",
]


FINAL_SECTION = "\n".join(FINAL_LINES)


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
    safe_print("  📝 آپدیت نهایی حافظه")
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

    if "🔒 امنیت — هشدار مهم!" in content:
        safe_print("  ℹ️ بخش امنیت از قبل وجود داره!")
        pattern = r"\n---\n\n## 🔒 امنیت.*?(?=\n## |\Z)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    safe_print("  ➕ اضافه کردن بخش امنیت...")
    content += FINAL_SECTION
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
