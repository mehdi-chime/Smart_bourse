"""
engines/mid_term_engine.py
موتور میان‌مدت - پیدا کردن سهام با روند صعودی و پتانسیل رشد ۲۰ تا ۵۰٪ در ۱ تا ۳ ماه
"""

import numpy as np
from datetime import datetime

class MidTermEngine:
    def __init__(self, data, config=None):
        """
        data: لیست سهام با اطلاعات کامل (قیمت، اندیکاتورها، ...)
        """
        self.data = data
        self.config = config or self.default_config()
        self.candidates = []

    def default_config(self):
        return {
            "min_volume": 20_000_000_000,          # حداقل حجم روزانه
            "min_price": 100,                       # حداقل قیمت (ریال)
            "rsi_min": 40,                          # RSI حداقل ۴۰
            "rsi_max": 65,                          # RSI حداکثر ۶۵ (برای خرید)
            "ma_50_trend": True,                    # قیمت بالای MA50 باشد
            "macd_trend": "Bullish",                # MACD صعودی
            "min_growth_potential": 20,             # حداقل پتانسیل رشد (درصد)
            "max_candidates": 10,                   # تعداد سهام برتر
            "weights": {
                "trend": 0.30,      # قدرت روند
                "rsi": 0.20,        # RSI در محدوده خرید
                "volume": 0.15,     # نقدشوندگی
                "macd": 0.20,       # سیگنال MACD
                "volatility": 0.15  # نوسان مناسب برای سود
            }
        }

    def calculate_volatility(self, prices):
        """محاسبه نوسان قیمت به صورت انحراف معیار"""
        if len(prices) < 10:
            return 0
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns)

    def analyze_stock(self, stock):
        """
        تحلیل یک سهم برای میان‌مدت
        """
        score = 0
        
        # ---------- ۱. RSI ----------
        rsi = stock.get('rsi', 50)
        if self.config["rsi_min"] <= rsi <= self.config["rsi_max"]:
            score += 10
        elif 30 <= rsi < self.config["rsi_min"]:
            score += 6  # oversold - پتانسیل برگشت
        else:
            score += 2

        # ---------- ۲. MACD ----------
        macd = stock.get('macd', {})
        if macd.get('Trend') == 'Bullish':
            score += 10
        elif macd.get('Trend') == 'Bearish':
            score += 3
        else:
            score += 5

        # ---------- ۳. روند (قیمت نسبت به MA50) ----------
        ma50 = stock.get('ma50', 0)
        price = stock.get('close_price', 0)
        if price > ma50 and self.config["ma_50_trend"]:
            score += 8
        elif price < ma50 and ma50 > 0:
            score += 2

        # ---------- ۴. حجم معاملات ----------
        volume = stock.get('volume', 0)
        if volume > self.config["min_volume"] * 2:
            score += 8
        elif volume > self.config["min_volume"]:
            score += 5
        else:
            score += 1

        # ---------- ۵. نوسان (Volatility) ----------
        prices = stock.get('price_history', [])
        if len(prices) > 20:
            vol = self.calculate_volatility(prices)
            stock['volatility'] = vol
            # نوسان ۱ تا ۳ درصد در روز معمولاً خوب است
            if 0.01 <= vol <= 0.03:
                score += 8
            elif vol < 0.01:
                score += 4
            else:
                score += 2

        # ---------- ۶. پتانسیل رشد (هدف قیمتی) ----------
        # بر اساس حمایت و مقاومت تخمین زده می‌شود
        sr = stock.get('support_resistance', {})
        resistance = sr.get('nearest_resistance', price * 1.2) if sr else price * 1.2
        if resistance > price:
            growth_potential = ((resistance - price) / price) * 100
        else:
            growth_potential = 0
        stock['growth_potential'] = round(growth_potential, 1)

        if growth_potential > self.config["min_growth_potential"]:
            score += 8
        elif growth_potential > 10:
            score += 4
        else:
            score += 1

        # وزن‌دهی نهایی
        weights = self.config["weights"]
        final_score = (
            score * 0.5 +  # امتیاز پایه
            (growth_potential / 10) * 2  # پتانسیل رشد
        )
        stock['mid_term_score'] = min(100, round(final_score * 1.5, 1))

        # اضافه کردن توصیه
        if stock['mid_term_score'] > 70:
            stock['recommendation'] = "🟢 خرید قوی"
        elif stock['mid_term_score'] > 55:
            stock['recommendation'] = "🟡 خرید با احتیاط"
        else:
            stock['recommendation'] = "🔴 صبر کن"

        return stock

    def get_candidates(self):
        """انتخاب ۱۰ سهم برتر برای میان‌مدت"""
        analyzed = [self.analyze_stock(s) for s in self.data if s.get('close_price', 0) > 0]
        sorted_stocks = sorted(analyzed, key=lambda x: x.get('mid_term_score', 0), reverse=True)
        self.candidates = sorted_stocks[:self.config["max_candidates"]]
        return self.candidates

    def report(self):
        """گزارش کامل موتور میان‌مدت"""
        if not self.candidates:
            return "❌ هیچ سهم مناسبی برای میان‌مدت پیدا نشد."

        lines = ["📊 گزارش موتور میان‌مدت (۱ تا ۳ ماه)"]
        lines.append("=" * 70)
        lines.append("")

        for i, stock in enumerate(self.candidates, 1):
            symbol = stock.get('symbol', 'نامشخص')
            price = stock.get('close_price', 0)
            score = stock.get('mid_term_score', 0)
            potential = stock.get('growth_potential', 0)
            rec = stock.get('recommendation', 'نامشخص')
            rsi = stock.get('rsi', 0)
            vol = stock.get('volatility', 0)

            lines.append(f"{i}. **{symbol}**")
            lines.append(f"   قیمت فعلی: {price:,.0f} ریال")
            lines.append(f"   RSI: {rsi:.1f}")
            lines.append(f"   نوسان روزانه: {vol:.2%}")
            lines.append(f"   پتانسیل رشد: {potential:.1f}%")
            lines.append(f"   امتیاز نهایی: {score:.1f}")
            lines.append(f"   توصیه: {rec}")
            
            # نمایش هدف قیمتی
            sr = stock.get('support_resistance', {})
            if sr:
                target = sr.get('nearest_resistance', price * 1.2)
                lines.append(f"   🎯 هدف قیمتی: {target:,.0f} ریال")
            
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)
