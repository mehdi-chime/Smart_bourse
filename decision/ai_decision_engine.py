"""
decision/ai_decision_engine.py
موتور تصمیم‌گیری هوشمند - ترکیب سیگنال‌ها و صدور دستور نهایی
"""

class AIDecisionEngine:
    def __init__(self, config=None):
        self.config = config or self.default_config()
        self.signals = []

    def default_config(self):
        return {
            "weights": {
                "order_flow": 0.25,
                "whale": 0.25,
                "technical": 0.20,
                "news": 0.15,
                "market_health": 0.15
            },
            "min_confidence": 0.6,
            "trade_fee": 0.0125
        }

    def add_signal(self, source, signal, confidence, data=None):
        """اضافه کردن یک سیگنال از یک منبع"""
        self.signals.append({
            "source": source,
            "signal": signal,  # BUY, SELL, HOLD
            "confidence": confidence,  # 0 تا ۱
            "data": data
        })

    def calculate_final_decision(self):
        """محاسبه تصمیم نهایی بر اساس وزن‌ها"""
        if not self.signals:
            return {"decision": "HOLD", "confidence": 0, "reason": "هیچ سیگنالی وجود ندارد"}

        buy_score = 0
        sell_score = 0
        total_weight = 0

        for signal in self.signals:
            source = signal["source"]
            weight = self.config["weights"].get(source, 0.1)
            total_weight += weight

            if signal["signal"] == "BUY":
                buy_score += weight * signal["confidence"]
            elif signal["signal"] == "SELL":
                sell_score += weight * signal["confidence"]
            # HOLD تأثیری در امتیاز ندارد

        # نرمال‌سازی
        if total_weight > 0:
            buy_score = buy_score / total_weight
            sell_score = sell_score / total_weight

        # تصمیم‌گیری
        if buy_score > sell_score and buy_score > self.config["min_confidence"]:
            decision = "BUY"
            confidence = buy_score
            reason = f"امتیاز خرید ({buy_score:.2f}) بیشتر از فروش ({sell_score:.2f}) است."
        elif sell_score > buy_score and sell_score > self.config["min_confidence"]:
            decision = "SELL"
            confidence = sell_score
            reason = f"امتیاز فروش ({sell_score:.2f}) بیشتر از خرید ({buy_score:.2f}) است."
        else:
            decision = "HOLD"
            confidence = max(buy_score, sell_score)
            reason = f"اطمینان کافی برای معامله وجود ندارد (خرید: {buy_score:.2f}, فروش: {sell_score:.2f})"

        return {
            "decision": decision,
            "confidence": confidence,
            "reason": reason,
            "buy_score": buy_score,
            "sell_score": sell_score,
            "signals": self.signals
        }

    def clear_signals(self):
        """پاک کردن سیگنال‌ها برای تحلیل بعدی"""
        self.signals = []

    def report(self):
        """گزارش تصمیم نهایی"""
        result = self.calculate_final_decision()
        lines = [
            "=" * 50,
            "🧠 تصمیم نهایی هوش مصنوعی",
            "=" * 50,
            f"تصمیم: {result['decision']}",
            f"اطمینان: {result['confidence']*100:.1f}%",
            f"دلیل: {result['reason']}",
            "",
            "📊 امتیازها:",
            f"   خرید: {result['buy_score']*100:.1f}%",
            f"   فروش: {result['sell_score']*100:.1f}%",
            "=" * 50
        ]
        return "\n".join(lines)


# ========== بخش تست ==========
if __name__ == "__main__":
    engine = AIDecisionEngine()

    # شبیه‌سازی سیگنال‌ها
    engine.add_signal("order_flow", "BUY", 0.8)
    engine.add_signal("whale", "BUY", 0.6)
    engine.add_signal("technical", "HOLD", 0.3)
    engine.add_signal("news", "BUY", 0.7)
    engine.add_signal("market_health", "SELL", 0.4)

    print(engine.report())
