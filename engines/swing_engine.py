"""
engines/swing_engine.py
موتور نوسان‌گیری روزانه - قیمت‌ها بر اساس ریال
"""

import json
from datetime import datetime

class SwingEngine:
    def __init__(self, data, config=None):
        self.data = data
        self.config = config or self.default_config()
        self.candidates = []

    def default_config(self):
        return {
            "min_volume": 50_000_000_000,
            "trade_fee": 0.0125,
            "min_profit": 0.02,
            "max_candidates": 3,
        }

    def filter_stocks(self):
        filtered = []
        for stock in self.data:
            volume = stock.get('volume', 0)
            change = abs(stock.get('change_percent', 0))
            if volume < self.config["min_volume"]:
                continue
            if change < 1.0:
                continue
            filtered.append(stock)
        return filtered

    def score_stock(self, stock):
        change = stock.get('change_percent', 0)
        volume = stock.get('volume', 0)
        score = 0
        if change < -2:
            score += 10
        elif -2 <= change < -0.5:
            score += 6
        elif 0.5 <= change < 2:
            score += 4
        elif change >= 2:
            score += 8
        volume_score = min(5, volume / 100_000_000_000)
        score += volume_score
        return round(score, 2)

    def get_candidates(self):
        filtered = self.filter_stocks()
        for stock in filtered:
            stock['score'] = self.score_stock(stock)
        sorted_stocks = sorted(filtered, key=lambda x: x.get('score', 0), reverse=True)
        self.candidates = sorted_stocks[:self.config["max_candidates"]]
        return self.candidates

    def report(self):
        if not self.candidates:
            return "❌ امروز هیچ سهم مناسبی برای نوسان‌گیری پیدا نشد."
        lines = ["📈 پیشنهادات نوسان‌گیری روزانه:"]
        for i, stock in enumerate(self.candidates, 1):
            symbol = stock.get('symbol', 'نامشخص')
            change = stock.get('change_percent', 0)
            volume = stock.get('volume', 0)
            score = stock.get('score', 0)
            price = stock.get('close_price', 0)
            if change < -1.5:
                signal = "🟢 خرید (افت قیمت)"
            elif change > 1.5:
                signal = "🔴 فروش (رشد قیمت)"
            else:
                signal = "🟡 نگهداری (نوسان کم)"
            lines.append(f"{i}. {symbol} | قیمت: {price:,.0f} ریال | تغییر: {change:+.2f}% | حجم: {volume:,} | امتیاز: {score} | {signal}")
        return "\n".join(lines)
