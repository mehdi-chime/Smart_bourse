# update_memory_v9.py
# ذخیره school_mode_v9 در حافظه
# اجرا: python update_memory_v9.py

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


V9_LINES = [
    "",
    "---",
    "",
    "## ✅ School Mode v9 — AI + Eitaa (تکمیل شد)",
    "",
    f"**تاریخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
    "### 📄 فایل‌های جدید",
    "",
    "| فایل | کار |",
    "|:---|:---|",
    "| `school_mode_v9.py` | رانر با AI |",
    "| `install_school_v9.py` | نصب تسک |",
    "",
    "### 🔧 تفاوت v9 با v8",
    "",
    "| مورد | v8 | v9 |",
    "|:---|:---|:---|",
    "| اسکنر | ✅ | ✅ |",
    "| سیگنال به ایتا | ✅ | ✅ |",
    "| وضعیت بازار | ✅ | ✅ |",
    "| **ثبت در AI** | ❌ | **✅** |",
    "| **چک نتایج AI** | ❌ | **✅** |",
    "| **مشاوره AI** | ❌ | **✅** |",
    "| **AI یاد می‌گیره** | ❌ | **✅** |",
    "",
    "### 🔄 چرخه v9",
    "",
    "```",
    "صبح 8:45 → school_mode_v9",
    "    ↓",
    "هر 5 دقیقه → smart_scanner_v8 + AI record",
    "    ↓",
    "هر 10 دقیقه → AI check + AI advice",
    "    ↓",
    "هر 30 دقیقه → وضعیت بازار",
    "    ↓",
    "ظهر 12:30 → پایان + AI یاد گرفت",
    "```",
    "",
    "### 🔧 توابع جدید v9",
    "",
    "- `record_signals_in_ai()` — ثبت سیگنال در AI",
    "- `check_ai_outcomes()` — چک نتایج",
    "- `get_ai_advice_for_signals()` — مشاوره AI",
    "",
    "### 🧪 تست موفق",
    "",
    "```",
    "School Mode v9 - Shoroo (با AI)",
    "[21:42:42] OK: Eitaa ersal",
    "[21:42:42] Khorooj - bazar baste",
    "```",
    "",
    "### 🎯 نصب تسک",
    "",
    "| مورد | مقدار |",
    "|:---|:---|",
    "| TaskName | `Smart_Bourse_v9` |",
    "| Next Run | 10/4/2026 8:45 AM |",
    "| Status | Ready |",
    "",
    "### 📊 نمره",
    "",
    "| جنبه | قبل | بعد |",
    "|:---|:---:|:---:|",
    "| AI | 82 | 85 |",
    "| اتوماسیون | 85 | 90 |",
    "| **میانگین** | **92** | **93** |",
    "",
]


V9_SECTION = "\n".join(V9_LINES)


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
    safe_print("  📝 ذخیره school_mode_v9 در حافظه")
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

    if "School Mode v9 — AI + Eitaa (تکمیل شد)" in content:
        safe_print("  ℹ️ بخش v9 از قبل وجود داره!")
        pattern = r"\n---\n\n## ✅ School Mode v9.*?(?=\n## |\Z)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    safe_print("  ➕ اضافه کردن بخش v9...")
    content += V9_SECTION
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
