# test_groq_v2.py
# تست همه مدل‌های Groq
# اجرا: python test_groq_v2.py

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


def test_model(token, model):
    """تست یه مدل"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "سلام"}],
        "max_tokens": 50,
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)

        if r.status_code == 200:
            result = r.json()
            text = result["choices"][0]["message"]["content"]
            return True, text[:80]
        else:
            return False, f"{r.status_code}: {r.text[:100]}"

    except Exception as e:
        return False, str(e)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🧪 تست همه مدل‌های Groq")
    safe_print("=" * 80)
    safe_print("")

    from config.llm_config import GROQ_API_KEY

    safe_print(f"  🔑 کلید: {GROQ_API_KEY[:20]}...")
    safe_print("")

    # لیست مدل‌های محتمل
    models = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "llama-3.2-1b-preview",
        "llama-3.2-3b-preview",
        "llama-3.2-11b-vision-preview",
        "llama-3.2-90b-vision-preview",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it",
    ]

    working = []

    for model in models:
        safe_print(f"  🔍 {model}...")

        success, result = test_model(GROQ_API_KEY, model)

        if success:
            safe_print(f"     ✅ موفق: {result}")
            working.append(model)
        else:
            safe_print(f"     ❌ {result}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")

    if working:
        safe_print(f"  ✅ {len(working)} مدل کار می‌کنه:")
        for m in working:
            safe_print(f"     - {m}")
    else:
        safe_print("  ❌ هیچ مدلی کار نکرد!")
        safe_print("  - Freegate روشن باشه")
        safe_print("  - توکن درست باشه")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
