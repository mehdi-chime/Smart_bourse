# install_roadmap_6.py
# نسخه‌ی ساده — بدون خطای triple quote
# اجرا: python install_roadmap_6.py

import os
import sys
import json
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
ROADMAP_DIR = PROJECT_ROOT / "roadmap_6"
PHASES_DIR = ROADMAP_DIR / "phases"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  نصب نقشه‌راه ۶ — بهترین در ایران")
    safe_print("=" * 70)
    safe_print("")

    # ===== قدم ۱: ساخت پوشه‌ها =====
    safe_print("[1] ساخت پوشه‌ها...")
    ROADMAP_DIR.mkdir(parents=True, exist_ok=True)
    PHASES_DIR.mkdir(parents=True, exist_ok=True)
    safe_print("   OK: " + str(ROADMAP_DIR))
    safe_print("   OK: " + str(PHASES_DIR))
    safe_print("")

    # ===== قدم ۲: ساخت ROADMAP_6.md =====
    safe_print("[2] ساخت ROADMAP_6.md...")

    roadmap_lines = []
    roadmap_lines.append("# نقشه‌راه ۶ — Smart_Bourse")
    roadmap_lines.append("")
    roadmap_lines.append("> نسخه: ۶.۰")
    roadmap_lines.append("> شعار: از بهترین ایران تا بهترین جهان")
    roadmap_lines.append("> هدف: نمره ۸.۶ → ۹.۵ در ایران")
    roadmap_lines.append("> وضعیت: شروع")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## اطلاعات کلی")
    roadmap_lines.append("")
    roadmap_lines.append("- سازنده: مهدی جلالی (معلم علوم + فروشگاه بازی فکری)")
    roadmap_lines.append("- مسیر پروژه: F:\\python\\har roz ba python\\smart_bours")
    roadmap_lines.append("- همکار: DeepSeek (Smart_Bourse2 + Smart_Bourse3)")
    roadmap_lines.append("- پروژه فعلی: ۱۷ فاز تکمیل شده، نمره ۹۵")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## هدف نهایی")
    roadmap_lines.append("")
    roadmap_lines.append("| معیار | فعلی | هدف |")
    roadmap_lines.append("|:---|:---:|:---:|")
    roadmap_lines.append("| نمره در ایران | ۸.۶ | ۹.۵ |")
    roadmap_lines.append("| AI | ۹۰٪ | ۹۵٪ |")
    roadmap_lines.append("| اتوماسیون | ۹۵٪ | ۹۸٪ |")
    roadmap_lines.append("| نوآوری | ۶۰٪ | ۹۰٪ |")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## فاز ۱: LLM Integration")
    roadmap_lines.append("")
    roadmap_lines.append("هدف: اضافه کردن LLM")
    roadmap_lines.append("زمان: ۱-۲ هفته")
    roadmap_lines.append("نمره: +۱")
    roadmap_lines.append("")
    roadmap_lines.append("کارها:")
    roadmap_lines.append("- ۱.۱ نصب DeepSeek API")
    roadmap_lines.append("- ۱.۲ ساخت llm_analyzer.py")
    roadmap_lines.append("- ۱.۳ تحلیل خبر با LLM")
    roadmap_lines.append("- ۱.۴ مشاوره‌ی متنی")
    roadmap_lines.append("- ۱.۵ گزارش هوشمند")
    roadmap_lines.append("- ۱.۶ ادغام با v10")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## فاز ۲: Multi-Agent AI")
    roadmap_lines.append("")
    roadmap_lines.append("هدف: سه AI با هم مشورت کنن")
    roadmap_lines.append("زمان: ۲ هفته")
    roadmap_lines.append("نمره: +۱")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## فاز ۳: تحلیل احساسات")
    roadmap_lines.append("")
    roadmap_lines.append("هدف: Fear & Greed Index")
    roadmap_lines.append("زمان: ۱ هفته")
    roadmap_lines.append("نمره: +۰.۵")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## فاز ۴: اتصال به کارگزاری")
    roadmap_lines.append("")
    roadmap_lines.append("هدف: معامله‌ی خودکار")
    roadmap_lines.append("زمان: ۲ هفته")
    roadmap_lines.append("نمره: +۰.۵")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## فاز ۵: بک‌تست حرفه‌ای")
    roadmap_lines.append("")
    roadmap_lines.append("هدف: Backtrader + ۱۰ سال داده")
    roadmap_lines.append("زمان: ۱ هفته")
    roadmap_lines.append("نمره: +۰.۵")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## فاز ۶: داشبورد حرفه‌ای")
    roadmap_lines.append("")
    roadmap_lines.append("هدف: Streamlit + API")
    roadmap_lines.append("زمان: ۱ هفته")
    roadmap_lines.append("نمره: +۰.۵")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## جدول زمانی")
    roadmap_lines.append("")
    roadmap_lines.append("| فاز | عنوان | مدت | هفته |")
    roadmap_lines.append("|:---:|:---|:---|:---|")
    roadmap_lines.append("| ۱ | LLM Integration | ۱-۲ هفته | ۱-۲ |")
    roadmap_lines.append("| ۲ | Multi-Agent | ۲ هفته | ۳-۴ |")
    roadmap_lines.append("| ۳ | احساسات | ۱ هفته | ۵ |")
    roadmap_lines.append("| ۴ | کارگزاری | ۲ هفته | ۶-۷ |")
    roadmap_lines.append("| ۵ | بک‌تست | ۱ هفته | ۸ |")
    roadmap_lines.append("| ۶ | داشبورد | ۱ هفته | ۹-۱۰ |")
    roadmap_lines.append("")
    roadmap_lines.append("جمع: ~۱۰ هفته (۲.۵ ماه)")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## نمره‌ی نهایی")
    roadmap_lines.append("")
    roadmap_lines.append("| فاز | نمره‌ی اضافه |")
    roadmap_lines.append("|:---:|:---:|")
    roadmap_lines.append("| ۱ | +۱ |")
    roadmap_lines.append("| ۲ | +۱ |")
    roadmap_lines.append("| ۳ | +۰.۵ |")
    roadmap_lines.append("| ۴ | +۰.۵ |")
    roadmap_lines.append("| ۵ | +۰.۵ |")
    roadmap_lines.append("| ۶ | +۰.۵ |")
    roadmap_lines.append("| جمع | +۴ |")
    roadmap_lines.append("")
    roadmap_lines.append("از ۸.۶ → ۹.۵ در ایران")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("## دو مورچه‌ی عاشق")
    roadmap_lines.append("")
    roadmap_lines.append("> با هم، آروم آروم، می‌ریم جلو.")
    roadmap_lines.append("> تو پشت‌کار، من علم و هنر.")
    roadmap_lines.append("> هدف: بهترین در ایران!")
    roadmap_lines.append("")
    roadmap_lines.append("---")
    roadmap_lines.append("")
    roadmap_lines.append("آخرین آپدیت: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    roadmap_lines.append("نسخه: ۶.۰")
    roadmap_lines.append("")

    roadmap_file = ROADMAP_DIR / "ROADMAP_6.md"
    roadmap_file.write_text("\n".join(roadmap_lines), encoding="utf-8")
    safe_print("   OK: " + str(roadmap_file))
    safe_print("")

    # ===== قدم ۳: ساخت TASKS.json =====
    safe_print("[3] ساخت TASKS.json...")

    tasks = {
        "version": "6.0",
        "created": datetime.now().isoformat(),
        "phases": [
            {"id": 1, "title": "LLM Integration", "weeks": 2, "score": 1.0, "status": "pending"},
            {"id": 2, "title": "Multi-Agent AI", "weeks": 2, "score": 1.0, "status": "pending"},
            {"id": 3, "title": "Sentiment Analysis", "weeks": 1, "score": 0.5, "status": "pending"},
            {"id": 4, "title": "Broker Integration", "weeks": 2, "score": 0.5, "status": "pending"},
            {"id": 5, "title": "Backtrader", "weeks": 1, "score": 0.5, "status": "pending"},
            {"id": 6, "title": "Dashboard", "weeks": 1, "score": 0.5, "status": "pending"},
        ]
    }

    tasks_file = ROADMAP_DIR / "TASKS.json"
    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    safe_print("   OK: " + str(tasks_file))
    safe_print("")

    # ===== قدم ۴: ساخت README.md =====
    safe_print("[4] ساخت README.md...")

    readme_lines = []
    readme_lines.append("# نقشه‌راه ۶ — راهنما")
    readme_lines.append("")
    readme_lines.append("## چیه؟")
    readme_lines.append("")
    readme_lines.append("نقشه‌راه ۶ برای رسیدن از ۸.۶ به ۹.۵ در ایران.")
    readme_lines.append("")
    readme_lines.append("## فازها")
    readme_lines.append("")
    readme_lines.append("| فاز | عنوان | زمان | نمره |")
    readme_lines.append("|:---:|:---|:---|:---:|")
    readme_lines.append("| ۱ | LLM Integration | ۲ هفته | +۱ |")
    readme_lines.append("| ۲ | Multi-Agent | ۲ هفته | +۱ |")
    readme_lines.append("| ۳ | احساسات | ۱ هفته | +۰.۵ |")
    readme_lines.append("| ۴ | کارگزاری | ۲ هفته | +۰.۵ |")
    readme_lines.append("| ۵ | بک‌تست | ۱ هفته | +۰.۵ |")
    readme_lines.append("| ۶ | داشبورد | ۱ هفته | +۰.۵ |")
    readme_lines.append("")
    readme_lines.append("## قوانین")
    readme_lines.append("")
    readme_lines.append("1. هر فاز دونه دونه")
    readme_lines.append("2. هر مرحله تست می‌شه")
    readme_lines.append("3. بعد OK → مرحله بعد")
    readme_lines.append("")
    readme_lines.append("## دو مورچه‌ی عاشق")
    readme_lines.append("")
    readme_lines.append("> با هم، آروم آروم، می‌ریم جلو.")
    readme_lines.append("")

    readme_file = ROADMAP_DIR / "README.md"
    readme_file.write_text("\n".join(readme_lines), encoding="utf-8")
    safe_print("   OK: " + str(readme_file))
    safe_print("")

    # ===== قدم ۵: ساخت پوشه‌های فاز =====
    safe_print("[5] ساخت پوشه‌های فاز...")
    for i in range(1, 7):
        phase_dir = PHASES_DIR / ("phase_" + str(i))
        phase_dir.mkdir(exist_ok=True)
        phase_readme = phase_dir / "README.md"
        phase_readme.write_text(
            "# فاز " + str(i) + "\n\nاین پوشه برای فاز " + str(i) + " نقشه‌راه ۶ است.\n",
            encoding="utf-8"
        )
        safe_print("   OK: phase_" + str(i) + "/")
    safe_print("")

    # ===== قدم ۶: چک نهایی =====
    safe_print("=" * 70)
    safe_print("  چک نهایی")
    safe_print("=" * 70)
    safe_print("")

    files = list(ROADMAP_DIR.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    dir_count = len([f for f in files if f.is_dir()])

    safe_print("  مسیر: " + str(ROADMAP_DIR))
    safe_print("  کل فایل‌ها: " + str(file_count))
    safe_print("  کل پوشه‌ها: " + str(dir_count))
    safe_print("")

    safe_print("=" * 70)
    safe_print("  نصب کامل شد!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("قدم بعدی:")
    safe_print("   1. برو توی Smart_Bourse3")
    safe_print("   2. بگو: بریم فاز ۱: LLM Integration")
    safe_print("")


if __name__ == "__main__":
    main()