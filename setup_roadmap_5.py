# setup_roadmap_5.py
# ساخت نقشه‌راه ۵ + آپدیت حافظه
# اجرا: python setup_roadmap_5.py

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
ROADMAP_FILE = PROJECT_ROOT / "ROADMAP_5.md"
BACKUP_DIR = PROJECT_ROOT / "backup" / "memory"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


# ═══════════════════════════════════════════════════════════
# محتوای ROADMAP_5.md
# ═══════════════════════════════════════════════════════════

ROADMAP_LINES = [
    "# 🗺️ نقشه‌راه ۵ — Smart_Bourse",
    "",
    "> نسخه: ۵.۰",
    "> شعار: از AI ضعیف تا AI یادگیرنده",
    "> هدف: دقت ۳۵٪ → ۶۵٪+",
    "> وضعیت: در حال اجرا",
    "",
    "---",
    "",
    "## 📌 اطلاعات کلی",
    "",
    "- **سازنده:** مهدی جلالی (معلم علوم + فروشگاه بازی فکری)",
    "- **مسیر پروژه:** F:\\python\\har roz ba python\\smart_bours",
    "- **همکار:** ChatGPT (شروع) + DeepSeek (تحلیل و بهبود)",
    "",
    "---",
    "",
    "## 🗺️ مقایسه‌ی نقشه‌راه‌ها",
    "",
    "### نقشه‌راه ۴ (قدیمی):",
    "",
    "| فاز | عنوان | مدت | وضعیت |",
    "|:---:|:---|:---|:---|",
    "| ۰ | تثبیت و پاکسازی | ۱ هفته | ❌ |",
    "| ۱ | حل مشکلات فوری | ۳ روز | ⚠️ |",
    "| ۲ | بازسازی AI | ۱ هفته | 🔄 |",
    "| ۳ | بهبود استراتژی | ۱ هفته | ❌ |",
    "| ۴ | اتوماسیون | ۱ هفته | ❌ |",
    "| ۵ | مستندسازی | ۳ روز | ❌ |",
    "| ۶ | تست خودکار | ۱ هفته | ❌ |",
    "",
    "**مشکل نقشه‌راه ۴:** خیلی کلی بود. هدف مشخص نبود.",
    "",
    "### نقشه‌راه ۵ (جدید):",
    "",
    "**تمرکز:** فقط روی AI و نقاط ضعف مشخص",
    "",
    "---",
    "",
    "## 🎯 نقشه‌راه ۵ — جدید",
    "",
    "### 🔴 فاز ۱: بازسازی AI (۱ هفته)",
    "",
    "**هدف:** دقت ۳۵٪ → ۵۵٪",
    "",
    "| مرحله | فایل | کار | تأثیر | زمان |",
    "|:---:|:---|:---|:---:|:---:|",
    "| ۱.۱ | ai/learner.py | بازسازی کامل | +۵٪ | ۱ روز |",
    "| ۱.۲ | ai/ai_engine.py | context فعال + RSI | +۵٪ | ۲ روز |",
    "| ۱.۳ | ai/memory.py | days_ago درست | +۲٪ | ۱ روز |",
    "| ۱.۴ | تست | تست AI جدید | — | ۱ روز |",
    "| ۱.۵ | مستندسازی | مستندات AI | — | ۱ روز |",
    "",
    "**خروجی فاز ۱:** AI با دقت ۵۰٪+",
    "",
    "---",
    "",
    "### 🟡 فاز ۲: ML واقعی (۱ هفته)",
    "",
    "**هدف:** دقت ۵۵٪ → ۶۵٪",
    "",
    "| مرحله | کار | تأثیر | زمان |",
    "|:---:|:---|:---:|:---:|",
    "| ۲.۱ | نصب Scikit-learn | — | ۱ روز |",
    "| ۲.۲ | RandomForest | +۵٪ | ۲ روز |",
    "| ۲.۳ | XGBoost | +۳٪ | ۲ روز |",
    "| ۲.۴ | Neural Network | +۲٪ | ۲ روز |",
    "",
    "**خروجی فاز ۲:** AI با دقت ۶۵٪+",
    "",
    "---",
    "",
    "### 🟢 فاز ۳: پاکسازی (۳ روز)",
    "",
    "**هدف:** کاهش فایل‌های اضافی",
    "",
    "| مرحله | کار | تأثیر |",
    "|:---:|:---|:---:|",
    "| ۳.۱ | ادغام نسخه‌ها (school_mode) | +۲ نمره |",
    "| ۳.۲ | ادغام نسخه‌ها (tomorrow) | +۲ نمره |",
    "| ۳.۳ | حذف # golden_scanner.py | +۱ نمره |",
    "| ۳.۴ | حذف swing_target.py.py | +۱ نمره |",
    "",
    "**خروجی فاز ۳:** ۱۵۰ فایل، ۰ تکراری",
    "",
    "---",
    "",
    "### 🔵 فاز ۴: مستندسازی (۳ روز)",
    "",
    "**هدف:** README حرفه‌ای",
    "",
    "| مرحله | کار |",
    "|:---:|:---|",
    "| ۴.۱ | README کامل |",
    "| ۴.۲ | CHANGELOG |",
    "| ۴.۳ | requirements.txt |",
    "| ۴.۴ | مستندات AI |",
    "",
    "---",
    "",
    "### 🟣 فاز ۵: تست خودکار (۱ هفته)",
    "",
    "**هدف:** Coverage > ۷۰٪",
    "",
    "| مرحله | کار |",
    "|:---:|:---|",
    "| ۵.۱ | pytest |",
    "| ۵.۲ | CI/CD |",
    "| ۵.۳ | Coverage |",
    "",
    "---",
    "",
    "## 📊 جدول زمانی",
    "",
    "| فاز | عنوان | مدت | هفته |",
    "|:---:|:---|:---|:---|",
    "| ۱ | بازسازی AI | ۱ هفته | هفته ۱ |",
    "| ۲ | ML واقعی | ۱ هفته | هفته ۲ |",
    "| ۳ | پاکسازی | ۳ روز | هفته ۳ |",
    "| ۴ | مستندسازی | ۳ روز | هفته ۳ |",
    "| ۵ | تست خودکار | ۱ هفته | هفته ۴ |",
    "",
    "**جمع:** ~۴ هفته",
    "",
    "---",
    "",
    "## 🎯 نقطه‌ی هدف (هدف نهایی)",
    "",
    "| معیار | فعلی | هدف |",
    "|:---|:---:|:---:|",
    "| دقت AI | ۳۵٪ | ۶۵٪+ |",
    "| SAFE_BUY | ۰٪ | ۵۰٪+ |",
    "| تعداد فایل‌ها | ۵۰۶ | ۱۵۰ |",
    "| خطوط کد | ۷۶,۴۶۹ | ۲۰,۰۰۰ |",
    "| مستندسازی | ۴۰٪ | ۹۰٪ |",
    "| تست | ۳۰٪ | ۷۰٪+ |",
    "| نمره‌ی کلی | ۷۲/۱۰۰ | ۹۰/۱۰۰+ |",
    "",
    "---",
    "",
    "## 🔍 نقطه‌ضعف‌ها (اولویت‌بندی شده)",
    "",
    "| اولویت | نقطه‌ضعف | نمره | راه‌حل |",
    "|:---:|:---|:---:|:---|",
    "| ۱ | AI ضعیف | ۵۵/۱۰۰ | فاز ۱ + ۲ |",
    "| ۲ | نسخه‌های پراکنده | ۵۰/۱۰۰ | فاز ۳ |",
    "| ۳ | مستندسازی | ۴۰/۱۰۰ | فاز ۴ |",
    "| ۴ | تست | ۳۰/۱۰۰ | فاز ۵ |",
    "| ۵ | داده‌ها | ۶۰/۱۰۰ | (بعداً) |",
    "",
    "---",
    "",
    "## 🎯 نقشه‌ی AI (فاز ۱ + ۲)",
    "",
    "### مرحله ۱.۱: ai/learner.py",
    "",
    "**مشکلات فعلی:**",
    "- یادگیری محافظه‌کاره (۰.۰۲)",
    "- فقط SAFE_BUY",
    "- فقط money_flow",
    "- حداقل ۲۰ نتیجه",
    "- حداقل ۵ نتیجه برای confidence",
    "",
    "**راه‌حل:**",
    "- همه دسته‌ها",
    "- همه وزن‌ها",
    "- تغییر بیشتر (۰.۰۵)",
    "- حداقل کمتر (۱۰)",
    "- confidence وزن‌دار",
    "",
    "### مرحله ۱.۲: ai/ai_engine.py",
    "",
    "**مشکلات فعلی:**",
    "- context همیشه ۵۰",
    "- RSI در امتیاز نیست",
    "- آستانه‌های نرم (-۲٪ = موفق)",
    "",
    "**راه‌حل:**",
    "- context فعال",
    "- RSI در امتیاز",
    "- آستانه‌ها سخت‌تر (+۱٪ = موفق)",
    "",
    "### مرحله ۱.۳: ai/memory.py",
    "",
    "**مشکلات فعلی:**",
    "- days_ago کار نمی‌کند",
    "",
    "**راه‌حل:**",
    "- days_ago درست",
    "",
    "### مرحله ۲.۱: ML واقعی",
    "",
    "**راه‌حل:**",
    "- Scikit-learn",
    "- RandomForest",
    "- XGBoost",
    "- Neural Network",
    "",
    "---",
    "",
    "## 📱 برای چت جدید",
    "",
    "**هر چت جدید، اول این دو فایل رو بفرست:**",
    "",
    "1. PROJECT_MEMORY.md",
    "2. ROADMAP_5.md",
    "",
    "**بعد بگو:**",
    "«بریم سراغ فاز ۱. اول ai/learner.py»",
    "",
    "---",
    "",
    "## 🎯 پیشرفت",
    "",
    "### ✅ انجام‌شده:",
    "",
    "- [x] تحلیل کامل پروژه",
    "- [x] تحلیل کامل AI",
    "- [x] شناسایی ۱۰ مشکل AI",
    "- [x] طراحی ۱۰ راه‌حل",
    "- [x] نقشه‌راه ۵",
    "",
    "### 🔄 در حال انجام:",
    "",
    "- [ ] فاز ۱: بازسازی AI",
    "",
    "### ❌ انجام نشده:",
    "",
    "- [ ] فاز ۲: ML واقعی",
    "- [ ] فاز ۳: پاکسازی",
    "- [ ] فاز ۴: مستندسازی",
    "- [ ] فاز ۵: تست خودکار",
    "",
    "---",
    "",
    "## 📊 نمره‌ی فعلی و هدف",
    "",
    "| جنبه | فعلی | هدف |",
    "|:---|:---:|:---:|",
    "| ایده | ۹۵ | ۹۵ |",
    "| استراتژی | ۸۵ | ۹۰ |",
    "| پیاده‌سازی | ۷۵ | ۸۵ |",
    "| ساختار | ۷۰ | ۸۵ |",
    "| AI | ۵۵ | ۸۵ |",
    "| مستندسازی | ۴۰ | ۹۰ |",
    "| کیفیت کد | ۷۰ | ۸۵ |",
    "| مقیاس | ۹۰ | ۹۰ |",
    "| پایداری | ۷۵ | ۸۵ |",
    "| آینده‌نگری | ۹۰ | ۹۵ |",
    "| میانگین | ۷۲ | ۹۰ |",
    "",
    "---",
    "",
    f"*آخرین آپدیت: {datetime.now().strftime('%Y-%m-%d')}*",
    "*نسخه: ۵.۰*",
    "*هدف: دقت AI از ۳۵٪ به ۶۵٪+*",
]

ROADMAP_CONTENT = "\n".join(ROADMAP_LINES)


# ═══════════════════════════════════════════════════════════
# بخش جدید برای PROJECT_MEMORY.md
# ═══════════════════════════════════════════════════════════

MEMORY_SECTION_LINES = [
    "",
    "---",
    "",
    "## 🗺️ نقشه‌راه ۵ (جدید)",
    "",
    "نقشه‌راه جدید در فایل `ROADMAP_5.md` ذخیره شده.",
    "",
    "**خلاصه:**",
    "",
    "| فاز | عنوان | مدت | هدف |",
    "|:---:|:---|:---|:---|",
    "| ۱ | بازسازی AI | ۱ هفته | دقت ۳۵٪ → ۵۵٪ |",
    "| ۲ | ML واقعی | ۱ هفته | دقت ۵۵٪ → ۶۵٪ |",
    "| ۳ | پاکسازی | ۳ روز | ۱۵۰ فایل |",
    "| ۴ | مستندسازی | ۳ روز | README کامل |",
    "| ۵ | تست خودکار | ۱ هفته | Coverage ۷۰٪+ |",
    "",
    "**هدف نهایی:** نمره از ۷۲ → ۹۰",
    "",
    "**نقطه‌ی هدف:**",
    "",
    "| معیار | فعلی | هدف |",
    "|:---|:---:|:---:|",
    "| دقت AI | ۳۵٪ | ۶۵٪+ |",
    "| SAFE_BUY | ۰٪ | ۵۰٪+ |",
    "| تعداد فایل‌ها | ۵۰۶ | ۱۵۰ |",
    "| نمره‌ی کلی | ۷۲ | ۹۰ |",
    "",
    "**برای چت جدید:**",
    "",
    "1. این فایل (PROJECT_MEMORY.md) رو بفرست",
    "2. فایل ROADMAP_5.md رو بفرست",
    "3. بگو: «بریم سراغ فاز ۱. اول ai/learner.py»",
    "",
]

MEMORY_SECTION = "\n".join(MEMORY_SECTION_LINES)


def backup_memory():
    """بکاپ از حافظه"""
    if not MEMORY_FILE.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"PROJECT_MEMORY_{timestamp}.md"
    content = MEMORY_FILE.read_text(encoding="utf-8")
    backup_file.write_text(content, encoding="utf-8")
    return backup_file


def create_roadmap():
    """ساخت ROADMAP_5.md"""
    ROADMAP_FILE.write_text(ROADMAP_CONTENT, encoding="utf-8")
    return len(ROADMAP_CONTENT)


def update_memory():
    """آپدیت PROJECT_MEMORY.md"""
    content = MEMORY_FILE.read_text(encoding="utf-8")

    # حذف بخش قدیمی (اگه هست)
    if "نقشه‌راه ۵ (جدید)" in content:
        pattern = r"\n---\n\n## 🗺️ نقشه‌راه ۵ \(جدید\).*?(?=\n## |\Z)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    # اضافه کردن بخش جدید
    content += MEMORY_SECTION

    # آپدیت تاریخ
    new_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(
        r"> آخرین آپدیت:.*",
        f"> آخرین آپدیت: {new_date}",
        content,
        count=1
    )

    MEMORY_FILE.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🗺️ ساخت نقشه‌راه ۵ + آپدیت حافظه")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بکاپ
    safe_print("  📦 بکاپ از حافظه...")
    backup = backup_memory()
    if backup:
        safe_print(f"     ✅ {backup.name}")
    safe_print("")

    # ۲. ساخت ROADMAP_5.md
    safe_print("  🗺️ ساخت ROADMAP_5.md...")
    roadmap_size = create_roadmap()
    safe_print(f"     ✅ {ROADMAP_FILE}")
    safe_print(f"     📏 {roadmap_size:,} کاراکتر")
    safe_print("")

    # ۳. آپدیت PROJECT_MEMORY.md
    safe_print("  🧠 آپدیت PROJECT_MEMORY.md...")
    memory_size = update_memory()
    safe_print(f"     ✅ {MEMORY_FILE}")
    safe_print(f"     📏 {memory_size:,} کاراکتر")
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ ROADMAP_5.md ساخته شد")
    safe_print("  ✅ PROJECT_MEMORY.md آپدیت شد")
    safe_print("")
    safe_print("  📁 فایل‌ها:")
    safe_print(f"     - {ROADMAP_FILE}")
    safe_print(f"     - {MEMORY_FILE}")
    if backup:
        safe_print(f"     - {backup}")
    safe_print("")
    safe_print("  🎯 قدم بعدی:")
    safe_print("     ۱. چت جدید باز کن")
    safe_print("     ۲. این دو فایل رو بفرست:")
    safe_print("        - PROJECT_MEMORY.md")
    safe_print("        - ROADMAP_5.md")
    safe_print("     ۳. بگو: «بریم سراغ فاز ۱»")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
