# ai/ai_news_bridge.py
# پل بین AI و ماژول خبر
# AI + News → تصمیم بهتر

import logging
from pathlib import Path
import sys

# لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# مسیر پروژه
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "news"))

from news_sentiment import NewsSentiment


class AINewsBridge:
    """اتصال AI به ماژول خبر"""

    def __init__(self):
        self.sentiment = NewsSentiment()
        # آخرین اخبار تحلیل شده
        self.latest_news = []

    def analyze_news(self, text):
        """تحلیل یه خبر"""
        analysis = self.sentiment.analyze_text(text)
        self.latest_news.append(analysis)
        return analysis

    def get_news_impact(self, symbol):
        """
        محاسبه تأثیر خبر روی یه سهم

        Returns:
            int: امتیاز تأثیر (مثبت یا منفی)
        """
        if not self.latest_news:
            return 0

        total_impact = 0
        for analysis in self.latest_news:
            symbols = analysis.get("symbols", [])
            # اگه سهم توی لیست تأثیرهاست یا "همه"
            if symbol in symbols or "همه" in symbols:
                total_impact += analysis.get("score", 0)

        return total_impact

    def apply_news_to_score(self, symbol, ai_score):
        """
        اعمال تأثیر خبر روی امتیاز AI

        Args:
            symbol: نماد
            ai_score: امتیاز AI

        Returns:
            dict: {
                "original_score": امتیاز اصلی,
                "news_impact": تأثیر خبر,
                "final_score": امتیاز نهایی,
                "has_news": آیا خبری هست,
                "warning": هشدار
            }
        """
        news_impact = self.get_news_impact(symbol)
        final_score = ai_score + news_impact

        # هشدار
        warning = None
        if news_impact <= -15:
            warning = "🔴 خبر بسیار منفی"
        elif news_impact <= -5:
            warning = "🟠 خبر منفی"
        elif news_impact >= 15:
            warning = "🟢 خبر بسیار مثبت"
        elif news_impact >= 5:
            warning = "🟡 خبر مثبت"

        return {
            "original_score": ai_score,
            "news_impact": news_impact,
            "final_score": final_score,
            "has_news": news_impact != 0,
            "warning": warning
        }

    def clear_news(self):
        """پاک کردن اخبار"""
        self.latest_news = []


# ===== تست =====
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 تست اتصال خبر به AI")
    print("=" * 60)
    print()

    bridge = AINewsBridge()

    # تست ۱: خبر تحریم
    print("📰 تست ۱: خبر تحریم...")
    bridge.analyze_news("امریکا تحریم‌های جدیدی علیه خودروسازی اعمال کرد. ایران‌خودرو و سایپا تحریم شدند.")
    result = bridge.apply_news_to_score("خگستر", 76.5)
    print(f"   امتیاز اصلی: {result['original_score']}")
    print(f"   تأثیر خبر: {result['news_impact']}")
    print(f"   امتیاز نهایی: {result['final_score']}")
    print(f"   هشدار: {result['warning']}")
    print()

    # تست ۲: خبر مثبت
    print("📰 تست ۲: خبر مثبت...")
    bridge.clear_news()
    bridge.analyze_news("توافق جدید بین ایران و آمریکا. مذاکرات برجام از سر گرفته شد.")
    result = bridge.apply_news_to_score("خگستر", 76.5)
    print(f"   امتیاز اصلی: {result['original_score']}")
    print(f"   تأثیر خبر: {result['news_impact']}")
    print(f"   امتیاز نهایی: {result['final_score']}")
    print(f"   هشدار: {result['warning']}")
    print()

    # تست ۳: هر دو خبر با هم
    print("📰 تست ۳: هر دو خبر با هم...")
    bridge.clear_news()
    bridge.analyze_news("توافق جدید بین ایران و آمریکا.")
    bridge.analyze_news("امریکا تحریم‌های جدیدی علیه خودروسازی اعمال کرد.")
    result = bridge.apply_news_to_score("خگستر", 76.5)
    print(f"   امتیاز اصلی: {result['original_score']}")
    print(f"   تأثیر خبر: {result['news_impact']}")
    print(f"   امتیاز نهایی: {result['final_score']}")
    print(f"   هشدار: {result['warning']}")
    print()

    print("=" * 60)
