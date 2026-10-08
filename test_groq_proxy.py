# test_groq_proxy.py
# تست Groq با proxy
# اجرا: python test_groq_proxy.py

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


def test_with_proxy(token, model, proxy):
    """تست با proxy"""
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

    proxies = {
        "http": proxy,
        "https": proxy,
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30,
            proxies=proxies,
        )

        if r.status_code == 200:
            result = r.json()
            text = result["choices"][0]["message"]["content"]
            return True, text[:80]
        else:
            return False, f"{r.status_code}: {r.text[:150]}"

    except Exception as e:
        return False, str(e)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🧪 تست Groq با Proxy")
    safe_print("=" * 80)
    safe_print("")

    from config.llm_config import GROQ_API_KEY

    safe_print(f"  🔑 کلید: {GROQ_API_KEY[:20]}...")
    safe_print("")

    # پروکسی‌های محتمل
    proxies = [
        ("Freegate 8580", "http://127.0.0.1:8580"),
        ("Freegate 8580 (https)", "https://127.0.0.1:8580"),
        ("Freegate 8080", "http://127.0.0.1:8080"),
        ("بدون proxy", None),
    ]

    models = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]

    for proxy_name, proxy_url in proxies:
        safe_print(f"  🌐 {proxy_name}")
        safe_print("")

        for model in models:
            safe_print(f"     🔍 {model}...")

            success, result = test_with_proxy(GROQ_API_KEY, model, proxy_url)

            if success:
                safe_print(f"        ✅ موفق: {result}")
                safe_print("")
                safe_print("=" * 80)
                safe_print(f"  🏆 پیدا شد!")
                safe_print(f"     Proxy: {proxy_url}")
                safe_print(f"     Model: {model}")
                safe_print("=" * 80)
                return
            else:
                safe_print(f"        ❌ {result[:80]}")

        safe_print("")

    safe_print("=" * 80)
    safe_print("  ❌ هیچ ترکیبی کار نکرد!")
    safe_print("")
    safe_print("  💡 راه‌حل‌ها:")
    safe_print("     1. Freegate روشن باشه")
    safe_print("     2. VPN دیگه امتحان کن")
    safe_print("     3. توکن رو دوباره چک کن")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
