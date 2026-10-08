# install_add_phases_7_8.py
# اضافه کردن فاز ۷ (صندوق) و ۸ (بورس کالا)
# اجرا: python install_add_phases_7_8.py

import os
import sys
import json
import shutil
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
    safe_print("  اضافه کردن فاز ۷ و ۸ به نقشه‌راه ۶")
    safe_print("=" * 70)
    safe_print("")

    # ===== قدم ۱: چک پوشه =====
    if not ROADMAP_DIR.exists():
        safe_print("ERROR: پوشه roadmap_6 پیدا نشد!")
        safe_print("اول install_roadmap_6.py رو اجرا کن.")
        input("Enter...")
        return

    # ===== قدم ۲: بکاپ =====
    safe_print("[1] بکاپ گرفتن...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = ROADMAP_DIR / "backup"
    backup_dir.mkdir(exist_ok=True)

    for fname in ["ROADMAP_6.md", "TASKS.json", "README.md"]:
        src = ROADMAP_DIR / fname
        if src.exists():
            dst = backup_dir / (fname.replace(".", "_") + "_" + timestamp + "." + fname.split(".")[-1])
            shutil.copy2(src, dst)
            safe_print("   OK: " + dst.name)
    safe_print("")

    # ===== قدم ۳: آپدیت ROADMAP_6.md =====
    safe_print("[2] آپدیت ROADMAP_6.md...")

    roadmap_file = ROADMAP_DIR / "ROADMAP_6.md"
    content = roadmap_file.read_text(encoding="utf-8")

    # چک کن قبلاً اضافه نشده
    if "فاز ۷" in content or "فاز 8" in content:
        safe_print("   ⚠️  فاز ۷ و ۸ قبلاً اضافه شدن!")
    else:
        # اضافه کردن فاز ۷ و ۸ قبل از "جدول زمانی"
        new_phases = []
        new_phases.append("")
        new_phases.append("---")
        new_phases.append("")
        new_phases.append("## فاز ۷: صندوق‌ها (ETF)")
        new_phases.append("")
        new_phases.append("**هدف:** اسکن و تحلیل صندوق‌های بورسی")
        new_phases.append("**زمان:** ۱ هفته")
        new_phases.append("**نمره:** +۰.۵")
        new_phases.append("")
        new_phases.append("### کارها:")
        new_phases.append("")
        new_phases.append("| # | کار | فایل |")
        new_phases.append("|:---:|:---|:---|")
        new_phases.append("| ۷.۱ | اسکن صندوق‌ها | `scanner/fund_scanner.py` |")
        new_phases.append("| ۷.۲ | محاسبه NAV | `scanner/fund_nav.py` |")
        new_phases.append("| ۷.۳ | حباب/کسر | `scanner/fund_premium.py` |")
        new_phases.append("| ۷.۴ | ادغام با v10 | `school_mode_v10.py` |")
        new_phases.append("")
        new_phases.append("### انواع صندوق‌ها:")
        new_phases.append("")
        new_phases.append("- **ETF سهامی** — مثل دواتکس")
        new_phases.append("- **ETF کالایی** — طلا، نفت")
        new_phases.append("- **صندوق درآمد ثابت** — کم‌ریسک")
        new_phases.append("- **صندوق اهرمی** — پرریسک")
        new_phases.append("")
        new_phases.append("---")
        new_phases.append("")
        new_phases.append("## فاز ۸: بورس کالا")
        new_phases.append("")
        new_phases.append("**هدف:** اسکن و تحلیل بورس کالا (IME)")
        new_phases.append("**زمان:** ۱ هفته")
        new_phases.append("**نمره:** +۰.۵")
        new_phases.append("")
        new_phases.append("### کارها:")
        new_phases.append("")
        new_phases.append("| # | کار | فایل |")
        new_phases.append("|:---:|:---|:---|")
        new_phases.append("| ۸.۱ | اتصال به IME | `market/ime_connector.py` |")
        new_phases.append("| ۸.۲ | داده‌ی کالا | `market/ime_data.py` |")
        new_phases.append("| ۸.۳ | تحلیل کالا | `market/commodity_analyzer.py` |")
        new_phases.append("| ۸.۴ | ادغام با v10 | `school_mode_v10.py` |")
        new_phases.append("")
        new_phases.append("### کالاهای مهم:")
        new_phases.append("")
        new_phases.append("- **فولاد** — بیشترین حجم")
        new_phases.append("- **پتروشیمی** — صادراتی")
        new_phases.append("- **سیمان** — ساخت‌وساز")
        new_phases.append("- **طلا** — امن")
        new_phases.append("- **قیر** — صادراتی")
        new_phases.append("")
        new_phases.append("---")
        new_phases.append("")

        # درج قبل از "جدول زمانی"
        marker = "## جدول زمانی"
        if marker in content:
            content = content.replace(marker, "\n".join(new_phases) + "\n" + marker)
            safe_print("   OK: فاز ۷ و ۸ اضافه شد")
        else:
            content += "\n".join(new_phases)
            safe_print("   OK: فاز ۷ و ۸ به آخر اضافه شد")

        # آپدیت جدول نمره
        if "| ۶ | داشبورد | ۱ هفته | ۹-۱۰ |" in content:
            content = content.replace(
                "| ۶ | داشبورد | ۱ هفته | ۹-۱۰ |",
                "| ۶ | داشبورد | ۱ هفته | ۹-۱۰ |\n"
                "| ۷ | صندوق‌ها | ۱ هفته | ۱۱ |\n"
                "| ۸ | بورس کالا | ۱ هفته | ۱۲ |"
            )

        roadmap_file.write_text(content, encoding="utf-8")

    safe_print("")

    # ===== قدم ۴: آپدیت TASKS.json =====
    safe_print("[3] آپدیت TASKS.json...")

    tasks_file = ROADMAP_DIR / "TASKS.json"
    if tasks_file.exists():
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        # چک کن قبلاً اضافه نشده
        existing_ids = [p["id"] for p in tasks.get("phases", [])]
        if 7 not in existing_ids:
            tasks["phases"].append({
                "id": 7,
                "title": "صندوق‌ها (ETF)",
                "weeks": 1,
                "score": 0.5,
                "status": "pending"
            })
        if 8 not in existing_ids:
            tasks["phases"].append({
                "id": 8,
                "title": "بورس کالا",
                "weeks": 1,
                "score": 0.5,
                "status": "pending"
            })

        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        safe_print("   OK: TASKS.json آپدیت شد")
    else:
        safe_print("   ERROR: TASKS.json پیدا نشد")
    safe_print("")

    # ===== قدم ۵: ساخت پوشه‌ها =====
    safe_print("[4] ساخت پوشه‌های phase_7 و phase_8...")
    for i in [7, 8]:
        phase_dir = PHASES_DIR / ("phase_" + str(i))
        phase_dir.mkdir(exist_ok=True)
        readme = phase_dir / "README.md"
        if i == 7:
            txt = "# فاز ۷ — صندوق‌ها (ETF)\n\nاسکن صندوق‌های بورسی + NAV + حباب/کسر\n"
        else:
            txt = "# فاز ۸ — بورس کالا\n\nاسکن IME + داده کالا + تحلیل\n"
        readme.write_text(txt, encoding="utf-8")
        safe_print("   OK: phase_" + str(i) + "/")
    safe_print("")

    # ===== قدم ۶: آپدیت README.md =====
    safe_print("[5] آپدیت README.md...")

    readme_file = ROADMAP_DIR / "README.md"
    content = readme_file.read_text(encoding="utf-8")

    if "فاز ۷" not in content:
        new_rows = []
        new_rows.append("| ۷ | صندوق‌ها | ۱ هفته | +۰.۵ |")
        new_rows.append("| ۸ | بورس کالا | ۱ هفته | +۰.۵ |")

        if "| ۶ | داشبورد | ۱ هفته | +۰.۵ |" in content:
            content = content.replace(
                "| ۶ | داشبورد | ۱ هفته | +۰.۵ |",
                "| ۶ | داشبورد | ۱ هفته | +۰.۵ |\n" + "\n".join(new_rows)
            )
            readme_file.write_text(content, encoding="utf-8")
            safe_print("   OK: README.md آپدیت شد")
        else:
            safe_print("   ⚠️  خط مورد نظر پیدا نشد")
    else:
        safe_print("   ⚠️  قبلاً اضافه شده")
    safe_print("")

    # ===== قدم ۷: چک نهایی =====
    safe_print("=" * 70)
    safe_print("  چک نهایی")
    safe_print("=" * 70)
    safe_print("")

    # فازها
    if tasks_file.exists():
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        phases = tasks.get("phases", [])
        safe_print("  فازهای نقشه‌راه ۶: " + str(len(phases)))
        total_score = sum(p.get("score", 0) for p in phases)
        safe_print("  جمع نمره: +" + str(total_score))
        safe_print("")
        for p in phases:
            safe_print("     فاز " + str(p["id"]) + ": " + p["title"] + " (نمره +" + str(p["score"]) + ")")

    safe_print("")
    safe_print("=" * 70)
    safe_print("  تمام شد!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📋 نتیجه:")
    safe_print("   • فاز ۷ (صندوق‌ها) اضافه شد")
    safe_print("   • فاز ۸ (بورس کالا) اضافه شد")
    safe_print("   • نمره نهایی: +۵")
    safe_print("   • نمره در ایران: ۹.۷/۱۰")
    safe_print("")
    input("  Enter...")


if __name__ == "__main__":
    main()
