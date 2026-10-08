# test_groq.py
# تست Groq
# اجرا: python test_groq.py

import os
import sys
import requests
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🧪 تست Groq")
    safe_print("=" * 80)
    safe_print("")

    # import
    try:
        from config.llm_config import GROQ_API_KEY
    except Exception as e:
        safe_print(f"  ❌ خطا در import: {e}")
        return

    safe_print(f"  🔑 کلید: {GROQ_API_KEY[:20]}...")
    safe_print("")

    # تست
    safe_print("  📡 ارسال درخواست...")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "سلام"}],
        "max_tokens": 50,
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        safe_print(f"  📊 Status: {r.status_code}")
        safe_print("")

        if r.status_code == 200:
            result = r.json()
            text = result["choices"][0]["message"]["content"]
            safe_print(f"  ✅ پاسخ: {text}")
        else:
            safe_print(f"  ❌ خطا: {r.text[:300]}")

    except Exception as e:
        safe_print(f"  ❌ خطا: {e}")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
