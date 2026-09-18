"""
test_eitaa.py
تست ارسال پیام به ایتا
"""

import requests

# ========== تنظیمات را از config.py بخوان ==========
try:
    from config import EITAA_TOKEN, EITAA_CHAT_ID
except ImportError:
    print("❌ فایل config.py پیدا نشد!")
    exit()

if not EITAA_TOKEN or not EITAA_CHAT_ID:
    print("❌ توکن یا chat_id در config.py خالی است!")
    exit()

# ========== ارسال پیام تست ==========
url = f"https://eitaa.com/bot{EITAA_TOKEN}/sendMessage"
params = {
    "chat_id": EITAA_CHAT_ID,
    "text": "✅ این یک پیام تست از Smart Bourse است.",
    "parse_mode": "HTML"
}

try:
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        print("✅ پیام با موفقیت به ایتا ارسال شد.")
        print(f"پاسخ: {response.text}")
    else:
        print(f"❌ خطا در ارسال: {response.status_code}")
        print(f"پاسخ: {response.text}")
except Exception as e:
    print(f"❌ خطا در اتصال به ایتا: {e}")
