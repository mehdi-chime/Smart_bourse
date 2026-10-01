# eitaa_news_reader.py
# خواندن کانال‌های ایتا (با ربات)
# اجرا: python eitaa_news_reader.py

import os
import sys
import json
import requests
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
sys.path.insert(0, str(PROJECT_ROOT))

# ═══════════════════════════════════════════════════════════
# تنظیمات
# ═══════════════════════════════════════════════════════════
sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
try:
    from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
except:
    EITAA_TOKEN = ""
    EITAA_CHAT_ID = ""

OUTPUT_DIR = PROJECT_ROOT / "data" / "eitaa_news"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# کلمات کلیدی بورسی
# ═══════════════════════════════════════════════════════════
KEYWORDS = [
    "بورس", "شاخص", "سهم", "قیمت", "خرید", "فروش",
    "صعود", "نزول", "مثبت", "منفی", "رشد", "ریزش",
    "توقف", "بازگشایی", "مجمع", "سود", "زیان",
    "افزایش سرمایه", "تعدیل", "پیش‌بینی", "کدال",
    "خبر", "تحلیل", "سیگنال", "هدف", "حمایت", "مقاومت",
    "دلار", "طلا", "نفت", "ارز", "تحریم", "مذاکره",
]

# ═══════════════════════════════════════════════════════════
# سهم‌های مهم
# ═══════════════════════════════════════════════════════════
IMPORTANT_STOCKS = [
    "فولاد", "خودرو", "خساپا", "شپنا", "فملی",
    "خگستر", "خپارس", "وبملت", "وتجارت", "شستا",
    "فارس", "شبریز", "پترول", "شتران", "کگل",
]


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def check_news_relevance(text):
    """چک کن خبر مربوط به بورسه یا نه"""
    text_lower = text.lower()
    score = 0
    found_keywords = []
    found_stocks = []

    for kw in KEYWORDS:
        if kw in text_lower:
            score += 1
            found_keywords.append(kw)

    for stock in IMPORTANT_STOCKS:
        if stock in text_lower:
            score += 3
            found_stocks.append(stock)

    return score, found_keywords, found_stocks


def check_news_sentiment(text):
    """تشخیص احساس خبر (مثبت/منفی/خنثی)"""
    positive_words = ["صعود", "رشد", "افزایش", "سود", "مثبت",
                     "بهبود", "برگشت", "خرید", "حمایت"]
    negative_words = ["نزول", "ریزش", "کاهش", "زیان", "منفی",
                     "افت", "توقف", "فروش", "مقاومت", "تحریم"]

    text_lower = text.lower()

    pos = sum(1 for w in positive_words if w in text_lower)
    neg = sum(1 for w in negative_words if w in text_lower)

    if pos > neg:
        return "مثبت", pos - neg
    elif neg > pos:
        return "منفی", neg - pos
    else:
        return "خنثی", 0


def verify_news(news_text):
    """صحت‌سنجی ساده"""
    # اینجا می‌شه با TSETMC، کدال مقایسه کرد
    result = {
        "relevant": False,
        "sentiment": "خنثی",
        "score": 0,
        "keywords": [],
        "stocks": [],
        "confidence": 0,
    }

    # چک مربوط بودن
    score, keywords, stocks = check_news_relevance(news_text)
    if score < 2:
        return result

    result["relevant"] = True
    result["score"] = score
    result["keywords"] = keywords
    result["stocks"] = stocks

    # چک احساس
    sentiment, strength = check_news_sentiment(news_text)
    result["sentiment"] = sentiment

    # اطمینان
    confidence = min(100, score * 5 + strength * 10)
    result["confidence"] = confidence

    return result


def main():
    safe_print("")
    safe_print("=" * 90)
    safe_print(f"  Eitaa News Reader")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 90)
    safe_print("")

    safe_print("  ⚠️ ایتا API عمومی نداره")
    safe_print("  ⚠️ فقط با ربات می‌شه")
    safe_print("")
    safe_print("  راه‌حل‌های ممکن:")
    safe_print("  ────────────────────")
    safe_print("  ۱. خودت پیام‌های مهم رو کپی کن")
    safe_print("     → اسکریپت تحلیل کنه")
    safe_print("")
    safe_print("  ۲. از کدال استفاده کن")
    safe_print("     → داده رسمی")
    safe_print("")
    safe_print("  ۳. از TSETMC استفاده کن")
    safe_print("     → داده بازار")
    safe_print("")
    safe_print("  ۴. ربات توی کانال ایتا")
    safe_print("     → نیاز به اجازه ادمین")
    safe_print("")

    # تست تحلیل یه خبر نمونه
    safe_print("=" * 90)
    safe_print("  تست تحلیل خبر:")
    safe_print("=" * 90)
    safe_print("")

    test_news = [
        "شاخص کل بورس امروز با رشد ۱۵ هزار واحدی به ۲ میلیون رسید",
        "فولاد امروز صف خرید شد، حجم معاملات بالا",
        "قیمت دلار افزایش یافت، تأثیر مثبت بر صادرات",
    ]

    for news in test_news:
        safe_print(f"  📰 خبر: {news[:60]}...")
        result = verify_news(news)
        safe_print(f"     مرتبط: {result['relevant']}")
        safe_print(f"     احساس: {result['sentiment']}")
        safe_print(f"     کلمات: {', '.join(result['keywords'][:5])}")
        safe_print(f"     سهم‌ها: {', '.join(result['stocks'])}")
        safe_print(f"     اطمینان: {result['confidence']}%")
        safe_print("")

    safe_print("=" * 90)
    safe_print("")


if __name__ == "__main__":
    main()
