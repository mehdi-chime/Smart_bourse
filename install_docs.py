# install_docs.py
# فاز ۴: مستندسازی
# اجرا: python install_docs.py

import os
import sys
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


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


# ═══════════════════════════════════════════════════════════
# README.md
# ═══════════════════════════════════════════════════════════

README_LINES = [
    "# 🎯 Smart_Bourse",
    "",
    "> سیستم تحلیل بورس ایران با AI یادگیرنده",
    "",
    "---",
    "",
    "## 📌 درباره",
    "",
    "Smart_Bourse یک سیستم تحلیل و معامله‌گری بورس ایران است که:",
    "",
    "- **هر روز** داده‌های بازار را جمع‌آوری می‌کند",
    "- **تحلیل** تکنیکال و بنیادی انجام می‌دهد",
    "- **سیگنال** خرید/فروش تولید می‌کند",
    "- **به ایتا** پیام می‌فرستد",
    "- **با AI** یاد می‌گیرد و بهتر می‌شود",
    "",
    "---",
    "",
    "## 🧠 فلسفه — شطرنج بورس",
    "",
    "> «مثل شطرنج: هر روز بازی کن، ضعف‌ها را بفهم، حذف کن.",
    "> AI هم همین: هر روز داده بگیر، تحلیل کن، بعد از یک سال خودش معامله کن.»",
    "",
    "---",
    "",
    "## 🎯 استراتژی",
    "",
    "```",
    "سهم‌هایی که RSI پایین دارند + در منفی 3% هستند",
    "    ↓",
    "بخر",
    "    ↓",
    "وقتی به مثبت 3% رسیدند",
    "    ↓",
    "بفروش",
    "```",
    "",
    "---",
    "",
    "## 📁 ساختار",
    "",
    "| پوشه | کار |",
    "|:---|:---|",
    "| `ai/` | موتور AI (ML، حافظه، یادگیری) |",
    "| `analysis/` | تحلیل |",
    "| `backtest/` | بک‌تست |",
    "| `core/` | هسته |",
    "| `data/` | داده‌ها |",
    "| `database/` | دیتابیس |",
    "| `engines/` | موتورها |",
    "| `indicators/` | اندیکاتورها |",
    "| `market/` | بازار |",
    "| `portfolio/` | پرتفوی |",
    "| `scanner/` | اسکنرها |",
    "| `strategy/` | استراتژی |",
    "| `utils/` | ابزار |",
    "",
    "---",
    "",
    "## 🚀 نصب",
    "",
    "```bash",
    "pip install -r requirements.txt",
    "```",
    "",
    "---",
    "",
    "## 🎮 اجرا",
    "",
    "```bash",
    "# منوی اصلی",
    "python smart_bourse_v10.py",
    "",
    "# اسکنر",
    "python smart_scanner_v8.py",
    "",
    "# حالت مدرسه",
    "python school_mode_v7.py",
    "",
    "# بررسی شبانه",
    "python night_check.py",
    "```",
    "",
    "---",
    "",
    "## 🤖 AI",
    "",
    "AI این سیستم شامل:",
    "",
    "- `ai_engine.py` — موتور اصلی (advise, check_outcomes)",
    "- `memory.py` — حافظه (JSONL)",
    "- `learner.py` — یادگیری (تنظیم وزن)",
    "- `ml_model.py` — مدل ML (RandomForest)",
    "- `trainer.py` — آموزش",
    "",
    "---",
    "",
    "## 📊 وضعیت",
    "",
    "| معیار | مقدار |",
    "|:---|:---:|",
    "| دقت AI | ~55% |",
    "| فایل‌های py | 505 |",
    "| خطوط کد | 76,000+ |",
    "| دیتابیس | 5 |",
    "",
    "---",
    "",
    "## 📝 مجوز",
    "",
    "Free for educational and personal use.",
    "",
    "---",
    "",
    "**Created by:** Mehdi Jalali",
    "**With collaboration:** DeepSeek AI",
    "",
    f"*آخرین آپدیت: {datetime.now().strftime('%Y-%m-%d')}*",
]


# ═══════════════════════════════════════════════════════════
# CHANGELOG.md
# ═══════════════════════════════════════════════════════════

CHANGELOG_LINES = [
    "# 📝 CHANGELOG",
    "",
    "## [5.0.0] — " + datetime.now().strftime("%Y-%m-%d"),
    "",
    "### ✅ فاز ۱ — بازسازی AI",
    "- `ai/learner.py` v2.0",
    "- `ai/ai_engine.py` v2.0",
    "- `ai/memory.py` v2.0",
    "",
    "### ✅ فاز ۲ — ML واقعی",
    "- `ai/ml_model.py` — RandomForest",
    "- `ai/trainer.py` — آموزش",
    "- `ai/ai_engine.py` v3.0 — ادغام ML",
    "",
    "### ✅ فاز ۳ — پاکسازی",
    "- آرشیو 10 فایل تکراری",
    "- آرشیو 2 پوشه اضافی",
    "",
    "---",
    "",
    "## [4.0.0] — قبل از بازسازی",
    "",
    "### ویژگی‌ها",
    "- 506 فایل py",
    "- 76,469 خط کد",
    "- AI v1.0 (بدون ML)",
    "- دقت ~35%",
]


# ═══════════════════════════════════════════════════════════
# requirements.txt
# ═══════════════════════════════════════════════════════════

REQUIREMENTS_LINES = [
    "# Smart_Bourse Requirements",
    "",
    "# Core",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "",
    "# Machine Learning",
    "scikit-learn>=1.3.0",
    "",
    "# Market Data",
    "algotik-tse>=1.0.0",
    "",
    "# Web / HTTP",
    "requests>=2.31.0",
    "",
    "# Excel",
    "openpyxl>=3.1.0",
    "",
    "# Selenium (اختیاری)",
    "# selenium>=4.15.0",
]


def write_file(path, lines):
    """نوشتن فایل"""
    content = "\n".join(lines)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📝 فاز ۴: مستندسازی")
    safe_print("=" * 80)
    safe_print("")

    # ۱. README.md
    safe_print("  📄 ساخت README.md...")
    size = write_file(PROJECT_ROOT / "README.md", README_LINES)
    safe_print(f"     ✅ {size:,} کاراکتر")
    safe_print("")

    # ۲. CHANGELOG.md
    safe_print("  📄 ساخت CHANGELOG.md...")
    size = write_file(PROJECT_ROOT / "CHANGELOG.md", CHANGELOG_LINES)
    safe_print(f"     ✅ {size:,} کاراکتر")
    safe_print("")

    # ۳. requirements.txt
    safe_print("  📄 ساخت requirements.txt...")
    size = write_file(PROJECT_ROOT / "requirements.txt", REQUIREMENTS_LINES)
    safe_print(f"     ✅ {size:,} کاراکتر")
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ README.md")
    safe_print("  ✅ CHANGELOG.md")
    safe_print("  ✅ requirements.txt")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
