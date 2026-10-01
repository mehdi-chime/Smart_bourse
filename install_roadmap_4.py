# install_roadmap_4.py
# نصب نقشه راه ۴ در Smart_Bourse
# اجرا: python install_roadmap_4.py

import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
ARCHIVE_DIR = ROOT / "docs" / "roadmap_archive"

# نقشه‌های قدیمی
OLD_ROADMAPS = [
    "Smart_Bourse_RoadMap.txt",
    "DeepSeek_RoadMap.txt",
    "DeepSeek_RoadMap_OLD.txt",
]

# محتوای نقشه راه ۴ — به صورت خط به خط (بدون مشکل یونیکد)
ROADMAP_4_LINES = [
    "# نقشه راه ۴ - Smart_Bourse",
    "",
    "> نسخه: ۴.۰",
    "> شعار: از هرج و مرج تا سیستم — از سیستم تا سود پایدار",
    "> وضعیت: در حال اجرا",
    "",
    "---",
    "",
    "## وضعیت فعلی (نقشه ۳)",
    "",
    "### موفقیت‌ها:",
    "- ۲۲۸ فایل پایتون",
    "- ۲۹,۵۵۵ خط کد",
    "- ۷ فاز کامل",
    "- AI با حافظه (۱۰۸ سیگنال)",
    "- پرتفوی ۲۶۵ میلیون تومان",
    "- سود ۴.۸٪ (دفرا)",
    "- وکغدیر +۷.۸٪",
    "",
    "### مشکلات:",
    "- AI: ۳۵٪ دقت",
    "- SAFE_BUY: ۰٪",
    "- ۱۱ فایل تکراری",
    "- مستندسازی ضعیف",
    "- ایتا: send_message نداره",
    "",
    "---",
    "",
    "## ۷ فاز جدید",
    "",
    "### فاز ۰: تثبیت و پاکسازی (۱ هفته)",
    "",
    "- ادغام ۱۱ فایل تکراری",
    "- حذف فایل‌های اضافی",
    "- ساختار منظم",
    "- مستندسازی پایه",
    "- requirements.txt کامل",
    "- README حرفه‌ای",
    "",
    "خروجی: ۱۵۰ فایل، ۰ تکراری",
    "",
    "### فاز ۱: حل مشکلات فوری (۳ روز)",
    "",
    "- حل مشکل ایتا",
    "- تحلیل پکویر",
    "- تست daily_runner",
    "- تست smart_alert",
    "- تست real_flow",
    "",
    "خروجی: ایتا کار می‌کنه",
    "",
    "### فاز ۲: بازسازی AI (۱ هفته)",
    "",
    "مشکل فعلی:",
    "- SAFE_BUY: 0/28 (0%)",
    "- SAFE_SELL: 36/76 (47%)",
    "",
    "اهداف:",
    "- فیلتر RSI برای SAFE_BUY (RSI < 65)",
    "- وزن‌دهی بهتر",
    "- یادگیری واقعی (ML)",
    "- بک‌تست AI",
    "",
    "معیار: SAFE_BUY > 50%",
    "",
    "### فاز ۳: بهبود استراتژی (۱ هفته)",
    "",
    "- hunter v55",
    "- analyze_top_signals v2",
    "- swing_engine v2",
    "- mid_term_engine v2",
    "- long_term_engine v2",
    "",
    "hunter v55:",
    "- RSI 15-50",
    "- MIN_RATIO = 1.5",
    "- MAX_RATIO = 10",
    "- حد ضرر -2% از خرید",
    "",
    "معیار: ۱۵-۲۰ سهم برتر",
    "",
    "### فاز ۴: اتوماسیون (۱ هفته)",
    "",
    "- حل ایتا",
    "- تلگرام (اختیاری)",
    "- زمان‌بند روزانه",
    "- پشتیبان خودکار",
    "",
    "زمان‌بندی:",
    "- 8:45 → auto_runner",
    "- 8:50 → hunter v55",
    "- 9:00 → سیگنال ایتا",
    "- 12:45 → پایان",
    "",
    "### فاز ۵: مستندسازی (۳ روز)",
    "",
    "- README حرفه‌ای",
    "- docs کامل",
    "- CHANGELOG",
    "- PROJECT_MEMORY",
    "",
    "### فاز ۶: تست خودکار (۱ هفته)",
    "",
    "- pytest",
    "- CI/CD",
    "- Coverage > 70%",
    "",
    "---",
    "",
    "## جدول زمانی",
    "",
    "| فاز | مدت | هفته |",
    "|-----|-----|------|",
    "| ۰. تثبیت | ۱ هفته | هفته ۱ |",
    "| ۱. فوری | ۳ روز | هفته ۲ |",
    "| ۲. AI | ۱ هفته | هفته ۲-۳ |",
    "| ۳. استراتژی | ۱ هفته | هفته ۳-۴ |",
    "| ۴. اتوماسیون | ۱ هفته | هفته ۴-۵ |",
    "| ۵. مستندسازی | ۳ روز | هفته ۵ |",
    "| ۶. تست | ۱ هفته | هفته ۵-۶ |",
    "",
    "جمع: ~۶ هفته",
    "",
    "---",
    "",
    "## اولویت‌بندی",
    "",
    "### فوری (این هفته):",
    "1. حل ایتا",
    "2. تحلیل پکویر",
    "3. تست daily_runner",
    "",
    "### مهم (۲ هفته):",
    "4. AI rebuild",
    "5. hunter v55",
    "6. پاکسازی",
    "",
    "### خوب (۱ ماه):",
    "7. اتوماسیون",
    "8. مستندسازی",
    "9. تست",
    "",
    "---",
    "",
    "## معیار موفقیت نهایی",
    "",
    "- ۱۵۰ فایل",
    "- ۲۰,۰۰۰ خط",
    "- AI دقت > 55%",
    "- SAFE_BUY > 50%",
    "- ایتا کار می‌کنه",
    "- اتوماسیون کامل",
    "- تست > 70%",
    "",
    "---",
    "",
    "*آخرین آپدیت: DATE_PLACEHOLDER*",
    "*نسخه: ۴.۰*",
    "",
]


def main():
    print()
    print("=" * 80)
    print("  نصب نقشه راه ۴")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # ۱. ساخت آرشیو
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    print("  [1/3] ساخت آرشیو...")
    print(f"     OK: {ARCHIVE_DIR}")
    print()

    # ۲. انتقال نقشه‌های قدیمی
    print("  [2/3] انتقال نقشه‌های قدیمی...")
    moved = 0
    for old in OLD_ROADMAPS:
        src = ROOT / old
        if src.exists():
            dst = ARCHIVE_DIR / old
            try:
                shutil.move(str(src), str(dst))
                print(f"     OK: {old}")
                moved += 1
            except Exception as e:
                print(f"     ERR: {old} - {e}")
        else:
            print(f"     SKIP: {old} (پیدا نشد)")
    print(f"     {moved} فایل منتقل شد")
    print()

    # ۳. ساخت ROADMAP_4.md
    print("  [3/3] ساخت ROADMAP_4.md...")
    roadmap_path = ROOT / "ROADMAP_4.md"

    # اضافه کردن تاریخ
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = "\n".join(ROADMAP_4_LINES)
    content = content.replace("DATE_PLACEHOLDER", date_str)

    with open(roadmap_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"     OK: {roadmap_path}")
    print(f"     {len(ROADMAP_4_LINES)} خط")
    print()

    # ۴. ساخت README آرشیو
    archive_readme = ARCHIVE_DIR / "README.md"
    archive_content = "# آرشیو نقشه راه‌ها\n\n"
    archive_content += "نقشه‌های قدیمی Smart_Bourse:\n\n"
    for old in OLD_ROADMAPS:
        archive_content += f"- {old}\n"
    archive_content += f"\nنقشه راه فعلی: ROADMAP_4.md\n"

    with open(archive_readme, 'w', encoding='utf-8') as f:
        f.write(archive_content)
    print(f"     OK: {archive_readme}")
    print()

    # ۵. خلاصه
    print("=" * 80)
    print("  نصب کامل شد!")
    print("=" * 80)
    print()
    print(f"  ROADMAP_4.md: {roadmap_path}")
    print(f"  Archive: {ARCHIVE_DIR}")
    print()
    print("  قدم بعدی:")
    print("     1. ROADMAP_4.md رو باز کن")
    print("     2. از فاز ۰ شروع کن")
    print()
    print("  دستور باز کردن:")
    print(f"     notepad {roadmap_path}")
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
