# setup_deepseek.py
# نصب و راه‌اندازی DeepSeek
# اجرا: python setup_deepseek.py

import os
import sys
import requests
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
CONFIG_DIR = PROJECT_ROOT / "config"
LLM_CONFIG_FILE = CONFIG_DIR / "llm_config.py"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def test_deepseek(token):
    """تست توکن DeepSeek"""
    safe_print("")
    safe_print("  🧪 تست توکن...")

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "سلام"}],
        "max_tokens": 50,
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)

        if r.status_code == 200:
            result = r.json()
            text = result["choices"][0]["message"]["content"]
            safe_print(f"     ✅ موفق!")
            safe_print(f"     پاسخ: {text[:100]}")
            return True
        elif r.status_code == 401:
            safe_print(f"     ❌ خطا: کلید اشتباهه!")
            return False
        elif r.status_code == 402:
            safe_print(f"     ❌ خطا: اعتبار صفر! (باید شارژ کنی)")
            return False
        elif r.status_code == 403:
            safe_print(f"     ❌ خطا: دسترسی نداره (VPN لازمه)")
            return False
        else:
            safe_print(f"     ❌ خطا: {r.status_code}")
            safe_print(f"     {r.text[:200]}")
            return False

    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        return False


def save_token(token):
    """ذخیره توکن توی llm_config.py"""
    safe_print("")
    safe_print("  💾 ذخیره توکن...")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if LLM_CONFIG_FILE.exists():
        content = LLM_CONFIG_FILE.read_text(encoding="utf-8")

        # جایگزین DEEPSEEK_API_KEY
        new_content = re.sub(
            r'DEEPSEEK_API_KEY\s*=\s*["\'].*?["\']',
            f'DEEPSEEK_API_KEY = "{token}"',
            content
        )

        if new_content == content:
            new_content = content + f'\nDEEPSEEK_API_KEY = "{token}"\n'

        # تنظیم LLM_MODE
        new_content = re.sub(
            r'LLM_MODE\s*=\s*["\'].*?["\']',
            'LLM_MODE = "deepseek"',
            new_content
        )

        LLM_CONFIG_FILE.write_text(new_content, encoding="utf-8")
        safe_print(f"     ✅ ذخیره شد: {LLM_CONFIG_FILE.name}")
        return True
    else:
        content = f'''# config/llm_config.py
# تنظیمات LLM

GROQ_API_KEY = ""
DEEPSEEK_API_KEY = "{token}"

LLM_MODE = "deepseek"

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

TIMEOUT = 30
MAX_TOKENS = 500
'''
        LLM_CONFIG_FILE.write_text(content, encoding="utf-8")
        safe_print(f"     ✅ فایل ساخته شد: {LLM_CONFIG_FILE}")
        return True


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 نصب DeepSeek")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  📌 راهنما:")
    safe_print("     1. برو به: https://platform.deepseek.com/")
    safe_print("     2. Sign Up (ثبت‌نام)")
    safe_print("     3. API Keys → Create API Key")
    safe_print("     4. کلید رو کپی کن (sk-...)")
    safe_print("     5. توی این برنامه پیست کن")
    safe_print("")
    safe_print("  💡 اگه اعتبار نداری:")
    safe_print("     - $5 (۵ دلار) = ۵ میلیون توکن")
    safe_print("     - کافیه برای ماه‌ها")
    safe_print("")

    safe_print("  🔑 توکن DeepSeek رو وارد کن:")
    safe_print("")

    try:
        token = input("  > ").strip()
    except (KeyboardInterrupt, EOFError):
        safe_print("\n  ❌ لغو شد")
        return

    if not token:
        safe_print("  ❌ توکن خالیه!")
        return

    if not token.startswith("sk-"):
        safe_print("  ⚠️ توکن باید با `sk-` شروع بشه")
        safe_print(f"     توکن تو: {token[:20]}...")
        safe_print("")
        safe_print("  ادامه می‌دی؟ (y/n)")

        try:
            confirm = input("  > ").strip().lower()
        except:
            return

        if confirm != "y":
            return

    safe_print("")
    safe_print(f"  ✅ توکن دریافت شد: {token[:20]}...")
    safe_print("")

    test_result = test_deepseek(token)

    if not test_result:
        safe_print("")
        safe_print("  ⚠️ تست موفق نبود!")
        safe_print("  دلایل احتمالی:")
        safe_print("     - اعتبار صفر (باید شارژ کنی)")
        safe_print("     - توکن اشتباهه")
        safe_print("")
        safe_print("  بازم ذخیره کنم؟ (y/n)")

        try:
            confirm = input("  > ").strip().lower()
        except:
            return

        if confirm != "y":
            return

    save_token(token)

    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print(f"  ✅ توکن: {token[:20]}...")
    safe_print(f"  ✅ فایل: {LLM_CONFIG_FILE}")
    safe_print(f"  ✅ تست: {'موفق' if test_result else 'ناموفق'}")
    safe_print("")

    if test_result:
        safe_print("  🎯 حالا می‌تونی از LLM استفاده کنی!")
        safe_print("")
        safe_print("  📌 تست:")
        safe_print("     python ai/llm_analyzer.py")
    else:
        safe_print("  ⚠️ ولی ذخیره شد")
        safe_print("  اعتبار شارژ کن و دوباره تست کن")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
