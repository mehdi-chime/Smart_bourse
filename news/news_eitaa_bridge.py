# news/news_eitaa_bridge.py
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
