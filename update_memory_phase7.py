# update_memory_phase7.py
# ذخیره فاز ۷ در حافظه
# اجرا: python update_memory_phase7.py

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


PHASE7_LINES = [
    "",
    "---",
    "",
    "## ✅ فاز ۷ — اتوماسیون کامل (تکمیل شد)",
    "",
    f"**تاریخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
    "### 📄 فایل‌های جدید",
    "",
    "| فایل | کار |",
    "|:---|:---|",
    "| `daily_ai_runner.py` | رانر روزانه AI |",
    "| `install_automation_task.py` | نصب تسک زمان‌بند |",
    "",
    "### 🔄 جریان کار",
    "",
    "```",
    "صبح 8:45 → school_mode_v7",
    "    ↓",
    "ظهر 12:30 → پایان معاملات",
    "    ↓",
    "13:00 → daily_ai_runner.py",
    "    ↓",
    "ثبت سیگنال‌ها در AI",
    "    ↓",
    "چک نتایج قبلی",
    "    ↓",
    "گزارش AI",
    "```",
    "",
    "### 📊 نتیجه‌ی تست",
    "",
    "- سیگنال‌های جدید: +15 (از 118 به 133)",
    "- Weights تغییر کرد (یادگیری فعال!)",
    "- `money_flow`: 0.40 → 0.419",
    "- `technical`: 0.35 → 0.349",
    "- `context`: 0.25 → 0.233",
    "",
    "### 🎯 دستورات",
    "",
    "```bash",
    "python daily_ai_runner.py",
    "python install_automation_task.py",
    "```",
    "",
    "---",
    "",
    "## 📊 نمره‌ی نهایی (فاز 7)",
    "",
    "| جنبه | قبل | بعد |",
    "|:---|:---:|:---:|",
    "| اتوماسیون | 60 | 85 |",
    "| **میانگین** | **88** | **89** |",
    "",
    "---",
    "",
    "## 📋 دستورالعمل چت جدید",
    "",
    "«فاز 1-7 تکمیل شد:",
    "- AI v3.0 با ML",
    "- 12/12 تست PASSED",
    "- دیتابیس 302,134 رکورد",
    "- اتوماسیون کامل",
    "",
    "نمره: 72 → 89",
    "",
    "لطفاً PROJECT_MEMORY.md و ROADMAP_5.md رو بخون.»",
    "",
]


PHASE7_SECTION = "\n".join(PHASE7_LINES)


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
    safe_print("  📝 ذخیره فاز ۷ در حافظه")
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

    if "فاز ۷ — اتوماسیون کامل (تکمیل شد)" in content:
        safe_print("  ℹ️ بخش فاز ۷ از قبل وجود داره!")
        pattern = r"\n---\n\n## ✅ فاز ۷ — اتوماسیون کامل \(تکمیل شد\).*?(?=\n## |\Z)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    safe_print("  ➕ اضافه کردن بخش فاز ۷...")
    content += PHASE7_SECTION
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
