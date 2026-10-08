# install_set_api_key.py
# جایگزینی خودکار API Key در llm_config.py
# اجرا: python install_set_api_key.py

import os
import sys
import re
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
CONFIG_FILE = PROJECT_ROOT / "config" / "llm_config.py"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  🔑 جایگزینی API Key در llm_config.py")
    safe_print("=" * 70)
    safe_print("")

    # ===== قدم ۱: چک فایل =====
    if not CONFIG_FILE.exists():
        safe_print(f"❌ فایل پیدا نشد: {CONFIG_FILE}")
        safe_print("   اول install_llm_phase1.py رو اجرا کن.")
        input("Enter...")
        return

    safe_print(f"✅ فایل پیدا شد: {CONFIG_FILE.name}")
    safe_print("")

    # ===== قدم ۲: بکاپ =====
    safe_print("[1] بکاپ گرفتن...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = CONFIG_FILE.with_suffix(f".py.bak_{timestamp}")
    shutil.copy2(CONFIG_FILE, backup_file)
    safe_print(f"   ✅ بکاپ: {backup_file.name}")
    safe_print("")

    # ===== قدم ۳: گرفتن کلید از کاربر =====
    safe_print("=" * 70)
    safe_print("  🔑 کلید DeepSeek رو وارد کن")
    safe_print("=" * 70)
    safe_print("")
    safe_print("  📌 کلید رو از https://platform.deepseek.com گرفتی")
    safe_print("  📌 با sk- شروع می‌شه")
    safe_print("  📌 طولش ~۵۰ کاراکتر")
    safe_print("")
    safe_print("  👇 کلید رو اینجا پیست کن (راست‌کلیک یا Ctrl+V):")
    safe_print("")

    # گرفتن کلید
    api_key = ""
    while not api_key:
        try:
            api_key = input("  🔑 API Key: ").strip()
        except (EOFError, KeyboardInterrupt):
            safe_print("\n❌ لغو شد.")
            return

        if not api_key:
            safe_print("  ⚠️  کلید خالیه! دوباره امتحان کن.")
            continue

        # چک کردن فرمت
        if not api_key.startswith("sk-"):
            safe_print(f"  ⚠️  کلید با sk- شروع نمی‌شه! مطمئنی؟")
            confirm = input("  ادامه بدهم؟ (y/n): ").strip().lower()
            if confirm != "y":
                api_key = ""
                continue

        if len(api_key) < 20:
            safe_print(f"  ⚠️  کلید خیلی کوتاهه ({len(api_key)} کاراکتر)! مطمئنی؟")
            confirm = input("  ادامه بدهم؟ (y/n): ").strip().lower()
            if confirm != "y":
                api_key = ""
                continue

    safe_print("")
    safe_print(f"  ✅ کلید دریافت شد ({len(api_key)} کاراکتر)")
    safe_print(f"  📌 شروع: {api_key[:10]}...")
    safe_print("")

    # ===== قدم ۴: خوندن فایل =====
    safe_print("[2] خوندن فایل...")
    content = CONFIG_FILE.read_text(encoding="utf-8")
    safe_print(f"   ✅ {len(content)} کاراکتر")
    safe_print("")

    # ===== قدم ۵: جایگزینی =====
    safe_print("[3] جایگزینی کلید...")

    # الگو: DEEPSEEK_API_KEY = ... (هر چیزی تا آخر خط)
    pattern = r'DEEPSEEK_API_KEY\s*=\s*.+'

    # خط جدید
    new_line = f'DEEPSEEK_API_KEY = "{api_key}"'

    # جایگزینی
    new_content = re.sub(pattern, new_line, content, count=1)

    if new_content == content:
        safe_print("   ⚠️  خط DEEPSEEK_API_KEY پیدا نشد!")
        safe_print("   📌 احتمالاً فایل دستکاری شده.")
        safe_print("")
        # اضافه کردن خط
        new_content = content + f'\n\n# اضافه شده\n{new_line}\n'
        safe_print("   ✅ خط جدید اضافه شد.")
    else:
        safe_print("   ✅ کلید جایگزین شد.")
    safe_print("")

    # ===== قدم ۶: ذخیره =====
    safe_print("[4] ذخیره فایل...")
    CONFIG_FILE.write_text(new_content, encoding="utf-8")
    safe_print(f"   ✅ ذخیره شد: {CONFIG_FILE.name}")
    safe_print("")

    # ===== قدم ۷: تست =====
    safe_print("=" * 70)
    safe_print("  🧪 تست خودکار")
    safe_print("=" * 70)
    safe_print("")

    test_code = """
import sys
sys.path.insert(0, r'F:\\python\\har roz ba python\\smart_bours')
from config.llm_config import DEEPSEEK_API_KEY

if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY.startswith('sk-'):
    print('RESULT: OK')
    print(f'KEY_LENGTH: {len(DEEPSEEK_API_KEY)}')
    print(f'KEY_START: {DEEPSEEK_API_KEY[:10]}...')
else:
    print('RESULT: FAIL')
    print(f'KEY: {DEEPSEEK_API_KEY[:20] if DEEPSEEK_API_KEY else "EMPTY"}')
"""

    # نوشتن تست موقت
    test_file = PROJECT_ROOT / "_test_key.py"
    test_file.write_text(test_code, encoding="utf-8")

    # اجرا
    result = os.popen(f'{sys.executable} "{test_file}"').read()
    safe_print(result)

    # پاک کردن تست
    try:
        test_file.unlink()
    except:
        pass

    # ===== قدم ۸: نتیجه =====
    safe_print("=" * 70)
    safe_print("  🎉 تمام!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📋 نتیجه:")
    safe_print("   • کلید توی llm_config.py ذخیره شد")
    safe_print("   • بکاپ: " + backup_file.name)
    safe_print("")
    safe_print("📋 قدم بعدی:")
    safe_print("   python ai\\llm_analyzer.py")
    safe_print("")

    input("  Enter برای خروج...")


if __name__ == "__main__":
    main()
