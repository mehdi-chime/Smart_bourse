# install_news_sentiment.py
# نصب خودکار ماژول تحلیل خبر
# اجرا: python install_news_sentiment.py

import os
import sys
from pathlib import Path

# ===== مسیرها =====
PROJECT_ROOT = Path(__file__).parent.absolute()
NEWS_DIR = PROJECT_ROOT / "news"
EITAA_DIR = PROJECT_ROOT / "eitaa"

print("=" * 60)
print("📰 نصب خودکار ماژول تحلیل خبر")
print("=" * 60)
print()

# ===== قدم ۱: ساخت پوشه news =====
print("📁 قدم ۱: ساخت پوشه news...")
NEWS_DIR.mkdir(exist_ok=True)
print(f"   ✅ آماده: {NEWS_DIR}")
print()

# ===== قدم ۲: ساخت news_sentiment.py =====
print("📝 قدم ۲: ساخت news/news_sentiment.py...")

sentiment_content = '''# news/news_sentiment.py
# تحلیل احساسات خبر
# تشخیص اخبار مهم و تأثیرشون روی سهم‌ها

import json
import logging
from pathlib import Path
from datetime import datetime

# لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# مسیر پروژه
PROJECT_ROOT = Path(__file__).parent.parent


# ===== کلمات کلیدی مهم =====
KEYWORDS = {
    "تحریم": {
        "weight": -10,
        "groups": ["خودرو", "فلزات", "بانک", "پتروشیمی", "ریلی"],
        "emoji": "🔴"
    },
    "تحریم‌های جدید": {
        "weight": -10,
        "groups": ["خودرو", "فلزات", "بانک", "پتروشیمی"],
        "emoji": "🔴"
    },
    "قطعنامه": {
        "weight": -5,
        "groups": ["بانک", "پتروشیمی"],
        "emoji": "🟠"
    },
    "مذاکره": {
        "weight": +5,
        "groups": ["بانک", "خودرو", "فلزات"],
        "emoji": "🟢"
    },
    "توافق": {
        "weight": +8,
        "groups": ["بانک", "خودرو", "فلزات", "پتروشیمی"],
        "emoji": "🟢"
    },
    "برجام": {
        "weight": +5,
        "groups": ["بانک", "خودرو", "فلزات"],
        "emoji": "🟢"
    },
    "افزایش سرمایه": {
        "weight": +3,
        "groups": ["همه"],
        "emoji": "🟢"
    },
    "توقف نماد": {
        "weight": -3,
        "groups": ["همه"],
        "emoji": "🟠"
    },
    "رشد دلار": {
        "weight": +5,
        "groups": ["صادرات", "فلزات", "پتروشیمی"],
        "emoji": "🟢"
    },
    "کاهش دلار": {
        "weight": -3,
        "groups": ["صادرات", "فلزات"],
        "emoji": "🟠"
    },
    "تورم": {
        "weight": -2,
        "groups": ["بانک", "خودرو"],
        "emoji": "🟠"
    },
    "رکورد شاخص": {
        "weight": +5,
        "groups": ["همه"],
        "emoji": "🟢"
    },
    "ریزش": {
        "weight": -5,
        "groups": ["همه"],
        "emoji": "🔴"
    },
    "صف فروش": {
        "weight": -3,
        "groups": ["همه"],
        "emoji": "🔴"
    },
    "صف خرید": {
        "weight": +3,
        "groups": ["همه"],
        "emoji": "🟢"
    },
}


# ===== سهم‌های هر گروه =====
GROUP_SYMBOLS = {
    "خودرو": ["خگستر", "خپارس", "خودرو", "سایپا", "پکویر", "ورنا"],
    "فلزات": ["فولاد", "فخوز", "ذوب", "فایرا", "فنورد"],
    "بانک": ["وبملت", "وتجارت", "وبصادر", "وپاسار"],
    "پتروشیمی": ["شپدیس", "شبصیر", "شغدیر", "پترول"],
    "ریلی": ["تراکتور", "وهپکو"],
    "صادرات": ["فولاد", "فخوز", "شپدیس"],
    "همه": [],
}


class NewsSentiment:
    """تحلیل احساسات خبر"""

    def __init__(self):
        self.news_file = PROJECT_ROOT / "data" / "news.jsonl"
        self.news_file.parent.mkdir(parents=True, exist_ok=True)

    def analyze_text(self, text):
        """
        تحلیل یه متن خبری

        Returns:
            dict: {
                "score": امتیاز کل,
                "keywords": کلمات پیدا شده,
                "groups": گروه‌های تحت تأثیر,
                "symbols": سهم‌های تحت تأثیر,
                "emoji": ایموجی
            }
        """
        text_lower = text.lower()
        found_keywords = []
        total_score = 0
        affected_groups = set()

        for keyword, info in KEYWORDS.items():
            if keyword in text:
                found_keywords.append(keyword)
                total_score += info["weight"]
                for g in info["groups"]:
                    affected_groups.add(g)

        # پیدا کردن سهم‌ها
        affected_symbols = []
        for group in affected_groups:
            if group == "همه":
                # همه سهم‌های watchlist
                affected_symbols.append("همه")
                break
            affected_symbols.extend(GROUP_SYMBOLS.get(group, []))

        # ایموجی
        if total_score <= -8:
            emoji = "🔴"
        elif total_score <= -3:
            emoji = "🟠"
        elif total_score >= 8:
            emoji = "🟢"
        elif total_score >= 3:
            emoji = "🟡"
        else:
            emoji = "⚪"

        return {
            "score": total_score,
            "keywords": found_keywords,
            "groups": list(affected_groups),
            "symbols": list(set(affected_symbols)),
            "emoji": emoji
        }

    def save_news(self, text, analysis):
        """ذخیره خبر"""
        news = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "analysis": analysis
        }
        with open(self.news_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(news, ensure_ascii=False) + "\\n")
        logger.info(f"✅ خبر ذخیره شد: {analysis['score']}")

    def format_alert(self, text, analysis):
        """ساخت پیام هشدار"""
        emoji = analysis["emoji"]
        score = analysis["score"]

        msg = f"{emoji} هشدار خبری {emoji}\\n\\n"
        msg += f"📰 خبر: {text[:200]}...\\n\\n"

        if analysis["keywords"]:
            msg += f"🔑 کلمات کلیدی: {', '.join(analysis['keywords'])}\\n\\n"

        msg += f"📊 امتیاز: {score:+d}\\n"

        if analysis["symbols"] and analysis["symbols"] != ["همه"]:
            msg += f"\\n🎯 سهم‌های تحت تأثیر:\\n"
            for sym in analysis["symbols"][:10]:
                msg += f"   • {sym}\\n"

        if score <= -5:
            msg += f"\\n⚠️ توصیه: احتیاط در خرید\\n"
        elif score >= 5:
            msg += f"\\n✅ توصیه: فرصت خرید\\n"

        msg += f"\\n⏰ Smart_Bourse"
        return msg


# ===== تست =====
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 تست تحلیل خبر")
    print("=" * 60)
    print()

    analyzer = NewsSentiment()

    # تست ۱: خبر تحریم
    print("📰 تست ۱: خبر تحریم خودروسازی...")
    news1 = "امریکا تحریم‌های جدیدی علیه خودروسازی ایران اعمال کرد. ایران‌خودرو و سایپا تحریم شدند."
    result1 = analyzer.analyze_text(news1)
    print(f"   امتیاز: {result1['score']}")
    print(f"   کلمات: {result1['keywords']}")
    print(f"   سهم‌ها: {result1['symbols'][:5]}")
    print()

    # تست ۲: خبر مثبت
    print("📰 تست ۲: خبر مثبت...")
    news2 = "توافق جدید بین ایران و آمریکا برای مذاکره. بازار بورس رکورد زد."
    result2 = analyzer.analyze_text(news2)
    print(f"   امتیاز: {result2['score']}")
    print(f"   کلمات: {result2['keywords']}")
    print()

    # تست ۳: پیام هشدار
    print("📰 تست ۳: پیام هشدار...")
    alert = analyzer.format_alert(news1, result1)
    print(alert)
    print()

    print("=" * 60)
'''

sentiment_file = NEWS_DIR / "news_sentiment.py"
sentiment_file.write_text(sentiment_content, encoding="utf-8")
print(f"   ✅ ساخته شد: {sentiment_file}")
print()

# ===== قدم ۳: ساخت __init__.py =====
print("📝 قدم ۳: ساخت news/__init__.py...")
init_file = NEWS_DIR / "__init__.py"
init_file.write_text("# news package\n", encoding="utf-8")
print(f"   ✅ ساخته شد")
print()

# ===== قدم ۴: ساخت news_eitaa_bridge.py =====
print("📝 قدم ۴: ساخت news/news_eitaa_bridge.py...")

bridge_content = '''# news/news_eitaa_bridge.py
# اتصال تحلیل خبر به ایتا

import sys
import logging
from pathlib import Path

# لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# مسیرها
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "eitaa"))
sys.path.insert(0, str(PROJECT_ROOT / "news"))

from news_sentiment import NewsSentiment
from ai_eitaa_bridge import EitaaBridge


class NewsAlerter:
    """هشدار خبری به ایتا"""

    def __init__(self):
        self.sentiment = NewsSentiment()
        self.bridge = EitaaBridge()

    def process_news(self, text, min_score=5):
        """
        پردازش یه خبر و ارسال به ایتا (اگه مهم بود)

        Args:
            text: متن خبر
            min_score: حداقل امتیاز برای ارسال (مثبت یا منفی)

        Returns:
            bool: ارسال شد یا نه
        """
        analysis = self.sentiment.analyze_text(text)

        # ذخیره
        self.sentiment.save_news(text, analysis)

        # اگه مهم نبود، ارسال نکن
        if abs(analysis["score"]) < min_score:
            logger.info(f"⚠️ خبر مهم نیست (امتیاز: {analysis['score']})")
            return False

        # ساخت پیام
        alert = self.sentiment.format_alert(text, analysis)

        # ارسال به ایتا
        result = self.bridge.send_message(alert)
        if result:
            logger.info(f"✅ هشدار خبری ارسال شد (امتیاز: {analysis['score']})")
        return result

    def process_batch(self, news_list, min_score=5):
        """پردازش چند خبر"""
        sent = 0
        for news in news_list:
            if self.process_news(news, min_score):
                sent += 1
        logger.info(f"✅ {sent} خبر از {len(news_list)} خبر ارسال شد")
        return sent


# ===== تست =====
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 تست هشدار خبری به ایتا")
    print("=" * 60)
    print()

    alerter = NewsAlerter()

    # تست ۱: خبر تحریم
    print("📰 تست ۱: خبر تحریم...")
    news1 = "امریکا تحریم‌های جدیدی علیه خودروسازی و فلزات ایران اعمال کرد. ایران‌خودرو، سایپا، هپکو تحریم شدند."
    result1 = alerter.process_news(news1, min_score=5)
    print(f"   نتیجه: {'✅ ارسال شد' if result1 else '❌ مهم نبود'}")
    print()

    # تست ۲: خبر بی‌اهمیت
    print("📰 تست ۲: خبر بی‌اهمیت...")
    news2 = "امروز هوا آفتابی است."
    result2 = alerter.process_news(news2, min_score=5)
    print(f"   نتیجه: {'✅ ارسال شد' if result2 else '❌ مهم نبود'}")
    print()

    # تست ۳: خبر مثبت
    print("📰 تست ۳: خبر مثبت...")
    news3 = "توافق جدید بین ایران و آمریکا. مذاکرات برجام از سر گرفته شد. بورس رکورد زد."
    result3 = alerter.process_news(news3, min_score=5)
    print(f"   نتیجه: {'✅ ارسال شد' if result3 else '❌ مهم نبود'}")
    print()

    print("=" * 60)
'''

news_bridge = NEWS_DIR / "news_eitaa_bridge.py"
news_bridge.write_text(bridge_content, encoding="utf-8")
print(f"   ✅ ساخته شد: {news_bridge}")
print()

# ===== قدم ۵: تست =====
print("=" * 60)
print("🎯 قدم ۵: تست کامل")
print("=" * 60)
print()

# تست ۱: تحلیل خبر
print("🧪 تست ۱: تحلیل خبر...")
os.chdir(NEWS_DIR)
os.system(f"{sys.executable} news_sentiment.py")
print()

# تست ۲: ارسال به ایتا
print("🧪 تست ۲: ارسال به ایتا...")
os.system(f"{sys.executable} news_eitaa_bridge.py")
print()

print("=" * 60)
print("🎉 نصب کامل شد!")
print("=" * 60)
print()
print("📋 قدم بعدی:")
print("   - پیام‌های ایتا رو چک کن")
print("   - اگه رسیدن → بریم اتصال به AI")
print()
