"""
Project : Smart_Bourse
File    : ai/ai_engine.py
Version : 1.0.0

Description :
    مغز AI
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
        pending = self.memory.get_pending_signals()
        checked = 0
        for p in pending:
            symbol = p["symbol"]
            price_signal = p.get("last_price")
            if not price_signal:
                continue
            try:
                price_1d = price_lookup_func(symbol, 1)
                price_3d = price_lookup_func(symbol, 3)
                price_7d = price_lookup_func(symbol, 7)
            except Exception:
                continue
            success = None
            cat = p["category"]
            if cat == "SAFE_BUY" and price_3d:
                success = price_3d > price_signal
            elif cat == "SAFE_SELL" and price_3d:
                success = price_3d < price_signal
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
        print("  🧠 Smart_Bourse AI — گزارش حافظه")
        print("=" * 70)
        m = insight["memory"]
        print()
        print("📚 حافظه:")
        print("   کل سیگنال‌ها     : " + str(m["total_signals"]))
        print("   نتایج چک‌شده     : " + str(m["total_outcomes"]))
        print("   در انتظار چک    : " + str(m["pending"]))
        print("   موفق            : " + str(m["success_count"]))
        print("   ناموفق           : " + str(m["failure_count"]))
        print()
        print("⚖️  وزن‌های یادگرفته:")
        for k, v in insight["weights"].items():
            print("   " + k.ljust(15) + " : " + str(round(v, 3)))
        if insight["category_stats"]:
            print()
            print("📊 آمار دسته‌ها:")
            for cat, s in insight["category_stats"].items():
                rate = s.get("success_rate", 0)
                print("   " + cat.ljust(12) + " : " + str(s["success"]) + "/" + str(s["total"]) + "  (" + str(round(rate * 100, 1)) + "%)")
        print("=" * 70)


if __name__ == "__main__":
    engine = AIEngine()
    engine.report()
