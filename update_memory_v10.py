# update_memory_v10.py
# آپدیت حافظه با v10
# اجرا: python update_memory_v10.py

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


V10_LINES = [
    "",
    "---",
    "",
    "## ✅ School Mode v10 (داینامیک) — 1405/07/16",
    "",
    f"**تاریخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
    "### 📄 فایل‌های جدید",
    "",
    "| فایل | کار |",
    "|:---|:---|",
    "| `school_mode_v10.py` | رانر داینامیک |",
    "| `install_school_v10.py` | نصب تسک |",
    "| `test_school_v10.py` | تست دستی |",
    "| `dynamic_filter.py` | فیلتر داینامیک |",
    "| `alert_manager.py` | هشدار خودکار |",
    "| `filter_golden.py` | فیلتر طلایی |",
    "| `filter_golden_v2.py` | +۳٪ |",
    "| `golden_filter_final.py` | نهایی |",
    "",
    "### 🎯 کشف بزرگ — فیلتر طلایی",
    "",
    "با ۴۷۸ سیگنال و success = +۳٪:",
    "",
    "| RSI | Win Rate |",
    "|:---|:---:|",
    "| < ۱۸ | ۲.۶٪ 🔴 |",
    "| ۱۸-۲۰ | ۱۰۰٪ (کم) |",
    "| ۲۰-۲۲ | ۵.۰٪ 🔴 |",
    "| **۲۲-۲۴** | **۷۴.۲٪** 🟢 |",
    "| **۲۴-۲۶** | **۱۰۰٪** 🎉 |",
    "| ۲۶-۲۸ | ۵۰.۰٪ |",
    "| **۲۲-۲۶** | **۸۷.۳٪** 🏆 |",
    "| **۲۲-۲۸** | **۸۵.۱٪** 🏆 |",
    "| ۲۸-۳۰ | ۲۶.۲٪ 🔴 |",
    "",
    "**نتیجه:** بازه طلایی **RSI 22-28** (Win Rate ~۸۵٪)",
    "",
    "### 🔄 v10 چطور کار می‌کنه",
    "",
    "```",
    "صبح 8:45 → school_mode_v10",
    "    ↓",
    "تحلیل بازار (مثبت/منفی)",
    "    ↓",
    "تنظیم بازه RSI داینامیک:",
    "   - خیلی داغ: 28-38",
    "   - داغ: 28-40",
    "   - معمولی: 25-35",
    "   - سرد: 22-30",
    "   - خیلی سرد: 18-28",
    "    ↓",
    "اسکن سهم‌ها + بهترین 5 → ایتا",
    "    ↓",
    "هر 30 دقیقه: اسکنر اصلی",
    "    ↓",
    "ظهر 12:30 → پایان",
    "```",
    "",
    "### 📁 تسک نصب شده",
    "",
    "| تسک | زمان | کار |",
    "|:---|:---:|:---|",
    "| `Smart_Bourse_v10` | 8:45 | رانر داینامیک |",
    "",
    "**تسک‌های قدیمی حذف شدن:**",
    "- v9",
    "- Refresh",
    "- v8",
    "- v7",
    "",
    "### 🎯 پرتفوی فعلی",
    "",
    "| سهم | تعداد | خرید | فعلی | سود |",
    "|:---|:---:|:---:|:---:|:---:|",
    "| **وتوصا** | 3,027 | 3,027 | 3,190 | +5.38% |",
    "| **چاپ** | 4,072 | 19,644 | 20,400 | +3.85% |",
    "| **خزر** | 52,068 | 2,082 | 2,120 | +1.83% |",
    "| **حفاری** | 34,327 | 5,857 | 5,710 | -2.51% |",
    "",
    "**💰 سود خالص: +۵۰۴,۳۴۸ تومان**",
    "",
    "### 📊 نمره",
    "",
    "| جنبه | قبل | بعد |",
    "|:---|:---:|:---:|",
    "| AI | 85 | 90 |",
    "| اتوماسیون | 90 | 95 |",
    "| **میانگین** | **93** | **95** |",
    "",
]


V10_SECTION = "\n".join(V10_LINES)


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
    safe_print("  📝 ذخیره v10 در حافظه")
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

    if "School Mode v10 (داینامیک)" in content:
        safe_print("  ℹ️ از قبل هست، حذف و اضافه مجدد...")
        pattern = r"\n---\n\n## ✅ School Mode v10.*?(?=\n## |\Z)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    safe_print("  ➕ اضافه کردن...")
    content += V10_SECTION
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
