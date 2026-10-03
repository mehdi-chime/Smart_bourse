# news/news_sentiment.py
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
            f.write(json.dumps(news, ensure_ascii=False) + "\n")
        logger.info(f"✅ خبر ذخیره شد: {analysis['score']}")

    def format_alert(self, text, analysis):
        """ساخت پیام هشدار"""
        emoji = analysis["emoji"]
        score = analysis["score"]

        msg = f"{emoji} هشدار خبری {emoji}\n\n"
        msg += f"📰 خبر: {text[:200]}...\n\n"

        if analysis["keywords"]:
            msg += f"🔑 کلمات کلیدی: {', '.join(analysis['keywords'])}\n\n"

        msg += f"📊 امتیاز: {score:+d}\n"

        if analysis["symbols"] and analysis["symbols"] != ["همه"]:
            msg += f"\n🎯 سهم‌های تحت تأثیر:\n"
            for sym in analysis["symbols"][:10]:
                msg += f"   • {sym}\n"

        if score <= -5:
            msg += f"\n⚠️ توصیه: احتیاط در خرید\n"
        elif score >= 5:
            msg += f"\n✅ توصیه: فرصت خرید\n"

        msg += f"\n⏰ Smart_Bourse"
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
