"""
analysis/trend.py
تشخیص روند بازار - شامل کلاس‌های Trend و TrendAnalyzer
"""

import numpy as np

class Trend:
    """کلاس اصلی برای تشخیص روند (برای سازگاری با analysis.py)"""
    def __init__(self, prices=None):
        self.prices = prices or []
        self.trend = "NEUTRAL"
        self.strength = 0

    def calculate(self, prices=None, lookback=20):
        if prices is None:
            prices = self.prices
        if len(prices) < lookback:
            return {
                'trend': 'NEUTRAL',
                'strength': 0,
                'description': 'داده‌های کافی وجود ندارد'
            }
        
        recent_prices = prices[-lookback:]
        current_price = prices[-1]
        avg_price = np.mean(recent_prices)

        if current_price > avg_price * 1.02:
            trend = "UP"
            strength = min(100, (current_price / avg_price - 1) * 100)
        elif current_price < avg_price * 0.98:
            trend = "DOWN"
            strength = min(100, (avg_price / current_price - 1) * 100)
        else:
            trend = "NEUTRAL"
            strength = 0

        return {
            'trend': trend,
            'strength': round(strength, 2),
            'current_price': current_price,
            'avg_price': round(avg_price, 2),
            'description': f"روند {trend} با قدرت {strength:.1f}%"
        }

class TrendAnalyzer:
    """کلاس جدید برای سازگاری با advanced_scanner.py"""
    def __init__(self):
        self.trend = "NEUTRAL"

    def analyze(self, prices, lookback=20):
        if len(prices) < lookback:
            return {
                'trend': 'NEUTRAL',
                'strength': 0,
                'description': 'داده‌های کافی وجود ندارد'
            }

        recent_prices = prices[-lookback:]
        current_price = prices[-1]
        avg_price = np.mean(recent_prices)

        if current_price > avg_price * 1.02:
            trend = "UP"
            strength = min(100, (current_price / avg_price - 1) * 100)
        elif current_price < avg_price * 0.98:
            trend = "DOWN"
            strength = min(100, (avg_price / current_price - 1) * 100)
        else:
            trend = "NEUTRAL"
            strength = 0

        x = np.arange(len(recent_prices))
        slope = np.polyfit(x, recent_prices, 1)[0]
        slope_strength = abs(slope) / np.mean(recent_prices) * 100

        return {
            'trend': trend,
            'strength': round(strength, 2),
            'slope': round(slope, 2),
            'slope_strength': round(slope_strength, 2),
            'current_price': current_price,
            'avg_price': round(avg_price, 2),
            'description': f"روند {trend} با قدرت {strength:.1f}%"
        }

    def get_trend(self, prices, lookback=20):
        return self.analyze(prices, lookback)
