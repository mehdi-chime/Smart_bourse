"""
Project : Smart_Bourse
File    : ai/ai_engine.py
Version : 2.0.0
Description :
    مغز AI — با چک نتیجه هوشمند (فقط وقتی زمانش رسیده)
"""

from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.memory import AIMemory
from ai.learner import AILearner


class AIEngine:

    def __init__(self):
        self.memory = AIMemory()
        self.learner = AILearner()

    def record_signal(self, trade_date, symbol, category, ratio,
                      rsi=None, technical_score=None, final_score=None,
                      last_price=None):
        self.memory.save_signal(
            trade_date=trade_date,
            symbol=symbol,
            category=category,
            ratio=ratio,
            rsi=rsi,
            technical_score=technical_score,
            final_score=final_score,
            last_price=last_price,
        )

    def check_outcomes(self, price_lookup_func):
        """
        چک کردن نتیجه‌ی سیگنال‌ها
        نکته مهم: فقط وقتی چک می‌کنه که واقعاً اون روزها گذشته باشه
        """
        pending = self.memory.get_pending_signals()
        checked = 0
        skipped = 0

        today = datetime.now().date()

        for p in pending:
            symbol = p["symbol"]
            price_signal = p.get("last_price")
            signal_date_str = p.get("date")

            if not price_signal or not signal_date_str:
                skipped += 1
                continue

            # محاسبه‌ی روزهای گذشته
            try:
                signal_date = datetime.strptime(str(signal_date_str), "%Y-%m-%d").date()
                days_passed = (today - signal_date).days
            except Exception:
                skipped += 1
                continue

            if days_passed < 1:
                # هنوز یه روز هم نگذشته
                skipped += 1
                continue

            # فقط اون قیمت‌هایی که زمانشون رسیده
            price_1d = None
            price_3d = None
            price_7d = None

            if days_passed >= 1:
                price_1d = price_lookup_func(symbol, 1)
            if days_passed >= 3:
                price_3d = price_lookup_func(symbol, 3)
            if days_passed >= 7:
                price_7d = price_lookup_func(symbol, 7)

            # تعیین موفقیت (اولویت: 7d > 3d > 1d)
            success = None
            cat = p["category"]

            for price_check in [price_7d, price_3d, price_1d]:
                if price_check:
                    if cat == "SAFE_BUY":
                        success = price_check > price_signal
                    elif cat == "SAFE_SELL":
                        success = price_check < price_signal
                    break

            # اگه هیچ قیمتی موجود نبود، رد کن
            if success is None:
                skipped += 1
                continue

            self.memory.save_outcome(
                trade_date=p["date"],
                symbol=symbol,
                category=cat,
                price_at_signal=price_signal,
                price_after_1d=price_1d,
                price_after_3d=price_3d,
                price_after_7d=price_7d,
                success=success,
            )
            checked += 1

        if skipped > 0:
            print("   (" + str(skipped) + " سیگنال هنوز زمانش نرسیده)")

        return checked

    def get_insight(self):
        stats = self.memory.stats()
        outcomes = self.memory.load_outcomes()
        category_stats = self.learner.learn_from_outcomes(outcomes)
        return {
            "memory": stats,
            "category_stats": category_stats,
            "weights": self.learner.weights,
        }

    def advise(self, symbol, category, ratio, rsi=None, technical_score=None):
        outcomes = self.memory.load_outcomes()
        confidence = self.learner.get_confidence(category, outcomes)
        mf_score = self._score_money_flow(ratio)
        tech_score = technical_score or 50
        w = self.learner.weights
        final = (
            w["money_flow"] * mf_score
            + w["technical"] * tech_score
            + w["context"] * 50
        )
        advice = self._make_advice(category, final, confidence, rsi)
        return {
            "symbol": symbol,
            "category": category,
            "ratio": ratio,
            "rsi": rsi,
            "final_score": round(final, 1),
            "confidence": round(confidence, 2),
            "weights": w,
            "advice": advice,
        }

    @staticmethod
    def _score_money_flow(ratio):
        if ratio >= 10:
            return 100
        elif ratio >= 5:
            return 85
        elif ratio >= 2:
            return 65
        elif ratio >= 1:
            return 50
        elif ratio >= 0.5:
            return 35
        elif ratio >= 0.2:
            return 20
        return 10

    @staticmethod
    def _make_advice(category, final_score, confidence, rsi):
        if rsi and rsi > 80:
            return "منتظر اصلاح بمان — سهم در اوج قیمت است"
        if rsi and rsi < 30 and category == "SAFE_BUY":
            return "فرصت خوب — فشار خرید حقیقی با اشباع فروش"
        if category == "SAFE_BUY":
            if final_score > 75 and confidence > 0.6:
                return "کاندید قوی — بررسی بیشتر"
            elif final_score > 60:
                return "کاندید متوسط — زیر نظر بگیر"
            else:
                return "ضعیف — احتمالاً ارزش ورود ندارد"
        if category == "SAFE_SELL":
            return "فشار فروش — احتمال ریزش"
        if category == "QUEUE_BUY":
            return "صف خرید — بررسی کن که واقعی است یا دام"
        return "معمولی — نیاز به بررسی بیشتر"

    def report(self):
        insight = self.get_insight()
        print()
        print("=" * 70)
        print("  Smart_Bourse AI — گزارش حافظه")
        print("=" * 70)
        m = insight["memory"]
        print()
        print("حافظه:")
        print("   کل سیگنال‌ها     : " + str(m["total_signals"]))
        print("   نتایج چک‌شده     : " + str(m["total_outcomes"]))
        print("   در انتظار چک    : " + str(m["pending"]))
        print("   موفق            : " + str(m["success_count"]))
        print("   ناموفق           : " + str(m["failure_count"]))
        print()
        print("وزن‌های یادگرفته:")
        for k, v in insight["weights"].items():
            print("   " + k.ljust(15) + " : " + str(round(v, 3)))
        if insight["category_stats"]:
            print()
            print("آمار دسته‌ها:")
            for cat, s in insight["category_stats"].items():
                rate = s.get("success_rate", 0)
                print("   " + cat.ljust(12) + " : " + str(s["success"]) + "/" + str(s["total"]) + "  (" + str(round(rate * 100, 1)) + "%)")
        print("=" * 70)


if __name__ == "__main__":
    engine = AIEngine()
    engine.report()
